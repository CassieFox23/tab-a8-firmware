import android.media.MediaDrm;
import java.lang.ref.WeakReference;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.nio.ByteBuffer;
import java.util.UUID;

public class WidevineProbe {
    static final UUID WIDEVINE = new UUID(0xedef8ba979d64aceL, 0xa3c827dcd51d21edL);

    static final int[] LEVELS = {
        MediaDrm.SECURITY_LEVEL_SW_SECURE_CRYPTO,
        MediaDrm.SECURITY_LEVEL_SW_SECURE_DECODE,
        MediaDrm.SECURITY_LEVEL_HW_SECURE_CRYPTO,
        MediaDrm.SECURITY_LEVEL_HW_SECURE_DECODE,
        MediaDrm.SECURITY_LEVEL_HW_SECURE_ALL,
    };

    static String level(int l) {
        if (l == MediaDrm.SECURITY_LEVEL_SW_SECURE_CRYPTO) return "SW_SECURE_CRYPTO (L3)";
        if (l == MediaDrm.SECURITY_LEVEL_SW_SECURE_DECODE) return "SW_SECURE_DECODE";
        if (l == MediaDrm.SECURITY_LEVEL_HW_SECURE_CRYPTO) return "HW_SECURE_CRYPTO (L2)";
        if (l == MediaDrm.SECURITY_LEVEL_HW_SECURE_DECODE) return "HW_SECURE_DECODE";
        if (l == MediaDrm.SECURITY_LEVEL_HW_SECURE_ALL) return "HW_SECURE_ALL (L1)";
        return "OTHER (" + l + ")";
    }

    static void line(String k, Object v) {
        System.out.println(k + "=" + v);
    }

    // app_process has no app, so the public constructor refuses (no package name).
    // Allocate the object bare and run its native setup with the shell's package.
    static MediaDrm openAsShell() throws Exception {
        Class<?> unsafeClass = Class.forName("sun.misc.Unsafe");
        Field f;
        try {
            f = unsafeClass.getDeclaredField("THE_ONE");
        } catch (NoSuchFieldException e) {
            f = unsafeClass.getDeclaredField("theUnsafe");
        }
        f.setAccessible(true);
        Object unsafe = f.get(null);
        Method alloc = unsafeClass.getMethod("allocateInstance", Class.class);
        MediaDrm drm = (MediaDrm) alloc.invoke(unsafe, MediaDrm.class);
        ByteBuffer b = ByteBuffer.allocate(16);
        b.putLong(WIDEVINE.getMostSignificantBits()).putLong(WIDEVINE.getLeastSignificantBits());
        Method setup = MediaDrm.class.getDeclaredMethod("native_setup", Object.class, byte[].class, String.class);
        setup.setAccessible(true);
        setup.invoke(drm, new WeakReference<>(drm), b.array(), "com.android.shell");
        return drm;
    }

    public static void main(String[] args) {
        try {
            line("schemeSupported", MediaDrm.isCryptoSchemeSupported(WIDEVINE));
        } catch (Throwable t) {
            line("schemeSupported", "ERROR " + t);
        }
        for (int l : LEVELS) {
            try {
                line("supportedAt " + level(l), MediaDrm.isCryptoSchemeSupported(WIDEVINE, "video/mp4", l));
            } catch (Throwable t) {
                line("supportedAt " + level(l), "ERROR " + t);
            }
        }
        MediaDrm drm;
        try {
            drm = openAsShell();
        } catch (Throwable t) {
            line("open", "ERROR " + t + (t.getCause() != null ? " cause " + t.getCause() : ""));
            System.exit(2);
            return;
        }
        String[] keys = {"securityLevel", "version", "vendor", "description", "systemId",
                "hdcpLevel", "maxHdcpLevel", "oemCryptoApiVersion", "algorithms",
                "maxNumberOfSessions", "usageReportingSupport"};
        for (String k : keys) {
            try {
                line(k, drm.getPropertyString(k));
            } catch (Throwable t) {
                line(k, "ERROR " + t);
            }
        }
        try {
            line("connectedHdcpLevel", drm.getConnectedHdcpLevel());
            line("maxHdcpLevelApi", drm.getMaxHdcpLevel());
        } catch (Throwable t) {
            line("hdcpApi", "ERROR " + t);
        }
        try {
            byte[] session = drm.openSession();
            line("sessionSecurityLevel", level(drm.getSecurityLevel(session)));
            drm.closeSession(session);
        } catch (Throwable t) {
            line("sessionSecurityLevel", "ERROR " + t);
        }
    }
}
