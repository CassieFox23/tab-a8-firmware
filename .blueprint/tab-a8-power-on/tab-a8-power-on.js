// What happens when you press power on a Galaxy Tab A8: a blueprint scene.
// Facts: Tab-A8-teardown.md ("the plain version", "what lk does about verified boot"), from a static read of the
// bootloader. Where the read did not reach, the sheet says "NOT READ" or leaves the thing out.
// The "but... so..." chain: power starts a relay, each piece checking the next; BUT something must say whether the
// owner unlocked the tablet, SO lk keeps a record and asks the secure world; BUT a locked tablet must not run a
// tampered system, SO the boot image goes to the secure world and comes back as a colour; BUT an unlocked tablet
// should be allowed to run something else, SO the check is skipped and the colour is orange; BUT a failed check
// must not boot, SO red drops to Download Mode.
// Part choices: see NOTES.md. Lint: node scripts/check.mjs this-file.js (run later, inside a VM).
BLUEPRINT.scene('tab-a8-power-on', {
  title: 'What happens when you press power on a Galaxy Tab A8',
  fig: 1,
  sheet: 'SHEET 1 OF 1',
  size: [800, 400],
  parts: [
    // top row, the relay: power -> SPL -> sml -> Trusty
    { id: 'power', kind: 'box', at: [70, 95], size: [84, 50], label: 'POWER ON', n: 1, lead: 'n', name: 'Power on', note: 'you press the power key' },
    { id: 'spl', kind: 'box', at: [200, 95], size: [84, 56], label: 'SPL', n: 2, lead: 'sw', name: 'SPL', note: 'the first small loader; what checks it is not in the files read' },
    { id: 'key', kind: 'key', at: [200, 38], labelAt: 'e', label: 'KEY FINGERPRINT', n: 3, lead: 'w', name: 'Key fingerprint', note: 'a key fingerprint the SPL carries; each piece it loads is checked against it' },
    { id: 'rack', kind: 'queue', at: [200, 190], size: [130, 30], slots: 4, count: 0, label: 'TEECFG SML\nTRUSTOS LK', n: 4, lead: 'ne', name: 'Next pieces', note: 'teecfg, sml, trustos and lk: the four pieces the SPL loads' },
    { id: 'sml', kind: 'box', at: [420, 95], size: [88, 50], label: 'SML', n: 5, lead: 'ne', name: 'sml', note: 'the secure-world monitor; it starts with Trusty, the secure world' },
    { id: 'zone', kind: 'zone', at: [650, 95], size: [170, 130], label: 'SECURE WORLD' },
    { id: 'trusty', kind: 'box', at: [650, 95], size: [100, 50], label: 'TRUSTY', n: 6, lead: 'ne', name: 'Trusty', note: 'the secure world; lk asks it two things (commands 0x33 and 0x20)' },
    // middle and bottom: lk and what it does
    { id: 'lk', kind: 'box', at: [420, 265], size: [100, 56], label: 'LK', n: 7, lead: 'sw', name: 'lk', note: 'the main bootloader; how control gets to it was not read' },
    { id: 'record', kind: 'book', at: [220, 265], label: 'MISCDATA', n: 8, lead: 'w', name: 'Unlock record', note: 'a small record in the miscdata partition' },
    { id: 'lamp', kind: 'lamp', at: [560, 265], on: 0, label: 'COLOUR', n: 9, lead: [34, -14], name: 'Boot state', note: 'green, yellow, orange or red; "green" and "yellow" are the names in the bootloader\'s own log lines' },
    { id: 'sieve', kind: 'sieve', at: [420, 345], labelAt: 'e', label: 'LK OWN\nCHECK', n: 10, lead: 'ne', name: 'lk\'s own check', note: 'always runs on the same signatures; the answer is logged and goes to the kernel command line, but does not set the colour' },
    { id: 'junc', kind: 'dot', at: [610, 265] },
    { id: 'android', kind: 'screen', at: [690, 265], size: [100, 70], label: 'ANDROID', n: 11, lead: 'ne', name: 'Android', note: 'gets the colour as androidboot.verifiedbootstate=green, yellow, orange or red' },
    { id: 'dl', kind: 'box', at: [610, 350], size: [110, 40], label: 'DOWNLOAD MODE', n: 12, lead: 'w', name: 'Download Mode', note: 'where red waits to be flashed; in the code as read it stays there' }
  ],
  lines: [
    { id: 'go', from: 'power.e', to: 'spl.w', arrow: true },
    { id: 'kw', from: 'key.s', to: 'spl.n', kind: 'wire' },
    { id: 'load', from: 'spl.s', to: 'rack.n', arrow: true },
    { id: 'jump', from: 'spl.e', to: 'sml.w', label: 'JUMPS TO', arrow: true },
    { id: 'start', from: 'sml.e', to: 'trusty.w', label: 'THEN', arrow: true },
    { id: 'hop', from: 'sml.s', to: 'lk.n', kind: 'wire', label: 'HAND-OFF: NOT READ', labelPos: 0.35 },
    { id: 'rd', from: 'record.e', to: 'lk.w', label: 'READS', arrow: true },
    { id: 'ask', from: 'lk.n+30', to: 'trusty.s', via: [[450, 200], [650, 200]], arrow: true },
    { id: 'colour', from: 'lk.e', to: 'lamp.w', arrow: true },
    { id: 'wk', from: 'lk.s', to: 'sieve.n', kind: 'wire' },
    { id: 'out1', from: 'lamp.e', to: 'junc' },
    { id: 'out2', from: 'junc', to: 'android.w', arrow: true },
    { id: 'jdl', from: 'junc.s', to: 'dl.n', arrow: true }
  ],
  steps: [
    {
      say: 'You press power (1), and the first small loader, the SPL (2), starts.',
      draw: ['power', 'go', 'spl'],
      note: { at: 'power.s', text: 'WHAT CHECKS\nTHE SPL:\nNOT READ', keep: true }
    },
    {
      say: 'It carries a key fingerprint (3), loads four pieces (4) and checks each one against it.',
      draw: ['kw', 'key', 'load', 'rack'],
      run: [
        { on: 'load', item: 'chip', text: 'TEECFG', dur: 0.6, arrive: { set: { rack: { count: 1 } } } },
        { on: 'load', item: 'chip', text: 'SML', dur: 0.6, arrive: { set: { rack: { count: 2 } } } },
        { on: 'load', item: 'chip', text: 'TRUSTOS', dur: 0.6, arrive: { set: { rack: { count: 3 } } } },
        { on: 'load', item: 'chip', text: 'LK', dur: 0.6, arrive: { set: { rack: { count: 4 } } } }
      ],
      glow: ['key']
    },
    {
      say: 'If a check fails it tries a backup copy, and if that fails too it stops in an endless loop.',
      fail: ['rack'],
      note: { at: 'rack.w', text: 'IF ONE FAILS:\nTRY BACKUP COPY;\nTHAT FAILS TOO:\nENDLESS LOOP' }
    },
    {
      say: 'Next the SPL jumps to sml (5), the secure-world monitor, which starts with Trusty (6).',
      view: ['spl', 'sml', 'zone'],
      draw: ['jump', 'sml', 'start', 'zone', 'trusty'],
      run: [
        { on: 'jump', item: 'ball', dur: 0.9 },
        { on: 'start', item: 'ball', dur: 0.9, arrive: { glow: ['trusty'] } }
      ]
    },
    {
      say: 'Then lk (7), the main bootloader, runs, but it must learn if the owner unlocked the tablet.',
      view: 'all',
      draw: ['hop', 'lk'],
      glow: ['lk']
    },
    {
      say: 'So lk reads a small record (8) and asks the secure world if it is genuine: locked or unlocked.',
      draw: ['rd', 'record', 'ask'],
      run: [
        { on: 'rd', item: 'chip', text: 'RECORD', dur: 0.9 },
        { on: 'ask', item: 'chip', text: '0x33', dur: 1.6, arrive: { glow: ['trusty'] } },
        { on: 'ask', back: true, item: 'chip', text: 'ANSWER', dur: 1.6 }
      ],
      note: { at: [478, 214], dx: 0, dy: 0, anchor: 'start', text: 'COMMAND 0x33:\nGENUINE RECORD?\nLOCKED/UNLOCKED' }
    },
    {
      say: 'But a locked tablet must not run a tampered system, so Trusty (6) checks its boot image.',
      draw: ['colour', 'lamp', 'wk', 'sieve'],
      run: [
        { on: 'ask', item: 'chip', text: 'BOOT IMAGE', dur: 1.6, arrive: { glow: ['trusty'] } },
        { on: 'ask', back: true, item: 'chip', text: 'GREEN', color: 'ok', dur: 1.6 },
        { on: 'colour', item: 'chip', text: 'GREEN', color: 'ok', dur: 0.9, arrive: { set: { lamp: { on: 1, text: 'GREEN' } }, glow: ['lamp'] } }
      ],
      note: [
        { at: [550, 200], dx: 0, dy: -8, anchor: 'middle', text: 'COMMAND 0x20' },
        { at: [478, 214], dx: 0, dy: 0, anchor: 'start', text: 'GREEN: SAMSUNG KEY\nYELLOW: OTHER KEY\nRED: ANYTHING ELSE' },
        { at: 'sieve.w', text: 'LOGGED, FEEDS\nTHE KERNEL\nCOMMAND LINE;\nNOT THE COLOUR', keep: true }
      ]
    },
    {
      say: 'But an unlocked tablet may run something else, so lk skips the check and the colour (9) is orange.',
      view: [270, 150, 530, 250],
      draw: ['out1', 'junc', 'out2', 'android'],
      set: { lamp: { on: 0, text: 'COLOUR' } },
      run: [
        { on: 'colour', item: 'chip', text: 'UNLOCKED', dur: 1.0, arrive: { set: { lamp: { on: 1, text: 'ORANGE' } }, glow: ['lamp'] } },
        { on: 'out1', item: 'ball', dur: 0.6 },
        { on: 'out2', item: 'ball', dur: 0.6, arrive: { glow: ['android'] } }
      ],
      note: [
        { at: [478, 214], dx: 0, dy: 0, anchor: 'start', text: 'NO 0x20 CHECK;\nORANGE WAITS A\nMOMENT, THEN BOOTS' },
        { at: [672, 322], dx: 0, dy: 0, anchor: 'start', text: 'GREEN OR YELLOW:\nLOGS A LINE,\nTHEN BOOTS' }
      ]
    },
    {
      say: 'But a failed check must not boot, so red prints a message and drops to Download Mode (12).',
      draw: ['jdl', 'dl'],
      set: { lamp: { on: 0, text: 'COLOUR' } },
      run: [
        { on: 'colour', item: 'chip', text: 'RED', color: 'fail', dur: 0.9, arrive: { set: { lamp: { on: 1, text: 'RED' } }, fail: ['lamp'] } },
        { on: 'out1', item: 'ball', color: 'fail', dur: 0.6 },
        { on: 'jdl', item: 'ball', color: 'fail', dur: 0.9, arrive: { glow: ['dl'] } }
      ],
      note: { at: 'dl.e', text: 'WAITS TO BE\nFLASHED; STAYS\nTHERE, AS READ' }
    },
    {
      say: 'Android (11) gets the colour; two unlocked tablets read orange and booted LineageOS.',
      view: 'all',
      set: { lamp: { on: 1, text: 'ORANGE' } },
      run: [
        { on: 'out1', item: 'ball', dur: 0.6 },
        { on: 'out2', item: 'ball', dur: 0.6, arrive: { set: { android: { text: 'LINEAGEOS' } } } }
      ],
      note: [
        { at: 'android.n', dx: -20, anchor: 'middle', text: 'SEEN ON 2 TABLETS' },
        { at: [672, 322], dx: 0, dy: 0, anchor: 'start', text: 'ANDROIDBOOT.\nVERIFIEDBOOTSTATE=\nGREEN, YELLOW,\nORANGE OR RED' }
      ],
      hold: 2.6
    }
  ]
});
