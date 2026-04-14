<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

This project implements a synchronous finite state machine (FSM) for a simplified washing machine cycle.

The design uses:

- a 1 Hz clock
- a weight sensor
- a water level sensor
- an internal 20-second timer

The washing cycle is divided into 9 states:

- `0000` Start
- `0001` Fill 1
- `0010` Wash
- `0011` Drain 1
- `0100` Fill 2
- `0101` Rinse
- `0110` Drain 2
- `0111` Spin
- `1000` Finish

Operation is as follows:

- In the `Start` state, the FSM checks the weight sensor.
  - If `P = 1`, overload is detected and the machine stays in `Start`.
  - If `P = 0`, the cycle begins and the machine moves to `Fill 1`.

- In `Fill 1` and `Fill 2`, the FSM waits until the water level sensor indicates full:
  - `A = 1` means full
  - `A = 0` means empty or not yet full

- In `Drain 1` and `Drain 2`, the FSM waits until the water level sensor indicates empty:
  - `A = 0` means empty

- In `Wash`, `Rinse`, and `Spin`, the FSM uses an internal counter.
  After 20 clock cycles, the timer-done signal becomes active and the FSM advances to the next state.
  Since the clock frequency is 1 Hz, each timed state lasts 20 seconds.

- In `Finish`, the FSM automatically returns to `Start`.

The reset input is active low (`rst_n`).
When reset is asserted, the FSM returns to `Start` and the timer counter is cleared.

## How to test

Use the following signals:

- `ui_in[0]` = `P` weight sensor
- `ui_in[1]` = `A` water level sensor

Outputs:

- `uo_out[3:0]` = current FSM state
- `uo_out[4]` = timer done signal
- `uo_out[7:5]` = unused

Recommended test procedure:

1. Apply reset by setting `rst_n = 0`.
   The FSM should go to state `0000`.

2. Release reset by setting `rst_n = 1`.

3. Set `P = 1`.
   The FSM should remain in `0000` (`Start`).

4. Set `P = 0`.
   On the next clock, the FSM should move to `0001` (`Fill 1`).

5. Keep `A = 0`.
   The FSM should remain in `0001`.

6. Set `A = 1`.
   On the next clock, the FSM should move to `0010` (`Wash`).

7. Wait 20 clock cycles.
   The FSM should move to `0011` (`Drain 1`).

8. Keep `A = 1`.
   The FSM should remain in `0011`.

9. Set `A = 0`.
   On the next clock, the FSM should move to `0100` (`Fill 2`).

10. Set `A = 1`.
    On the next clock, the FSM should move to `0101` (`Rinse`).

11. Wait 20 clock cycles.
    The FSM should move to `0110` (`Drain 2`).

12. Keep `A = 1`.
    The FSM should remain in `0110`.

13. Set `A = 0`.
    On the next clock, the FSM should move to `0111` (`Spin`).

14. Wait 20 clock cycles.
    The FSM should move to `1000` (`Finish`).

15. On the next clock, the FSM should return to `0000` (`Start`).

## External hardware

This design does not require external hardware.

For testing, two digital input switches can be used to emulate the sensors:

- one switch for the weight sensor `P`
- one switch for the water level sensor `A`

Optional LEDs can be connected to the outputs to observe the current state and timer-done signal.
