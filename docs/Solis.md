from google ai

# Collector

TOTAL_WTIME: The total accumulated working time of the data logger in seconds (e.g., 90031 seconds).

CURRENT_WTIME: The working time in seconds since the logger was last powered on or checked in.

COLLECTOR_VER: The current firmware version running on your Solis Wi-Fi/LAN stick (e.g., "1001318C").

RSSI: The received signal strength indicator (Wi-Fi strength) of your data logger.

WORKMODE: The current operating status code of the logger (e.g., 16). 

# Inverter

APPARENT_POWER: Refers to the total power flowing through your electrical system (measured in Volt-Amperes, or VA). It is the combination of Active Power (the actual usable power, measured in Watts) and Reactive Power (unused, circulating power).

DC_TOTALPOWER: The total direct current (DC) power generated, measured in Watts (W). It shows the total electrical power supplied to the inverter by 
your solar panels before any power conversion takes place.
f
REACTIVE_POWER: Is managed to stabilize the local electrical grid and correct voltage fluctuations. It is measured in VARs (Volt-Amperes Reactive) and works by adjusting the power factor (the phase alignment between grid voltage and current) so the inverter can either generate or absorb power as needed

PAC: The active output power of the inverter, measured in kiloWatts. This is the actual electricity currently generated and fed into your home or the power grid (kW)

FAC: The frequency of the AC grid connection, measured in Hertz (Hz).

U_PV: DC Voltage (U) from PV (PhotoVoltaic or solar) panels (V).
I_PV: DC Current (I) from panels (A).

U_AC: Alternating Current Voltage(U) (V).
I_AC: Alternating Current Current(I) (A).

U_MPPT: DC Voltage(U) Maximum Power Point Tracking (V).
I_MPTT: DC Current(I) Maximum Power Point Tracking (A).

MPTT: Maximum Power Point Tracking. Algorithm built into the inverter that constantly adjusts the voltage and current coming from your solar panels

# Advanced Settings

Power Control Mode: fines the inverter’s operational mode for voltage and reactive power management. Options include:
Default: Fixed-PF (Fixed Power Factor)

Remote Control: DRM (Demand Response Mode) functions allow utility companies or safety devices to remotely control or shut down an inverter's power output. A "DRM 008" or "REG0" state on your DRM system indicates that the inverter is under an active external shutdown/disconnect command

# Alarm codes

WARNING_INFO_DATA

Inverter hex value if there are system warnings or faults, e.g. '3F2' = 10101.

0 = Normal

| Message | Code | Description
|---------|------|-------------
| OV-G-V  | 1010 | Over grid voltage 
| UN-G-V  | 1011 | Under grid voltages
| OV-G-F  | 1012 | Grid frequency is higher than the set limit
| UN-G-F  | 1013 | Grid frequency is lower than the set limit
| Backfeed_Iac | 1014 | AC backfeed current is detected
| NO-Grid | 1015 | The inverter does not detect the utility grid


Complete list:
https://usservice.solisinverters.com/support/solutions/articles/73000560423-solis-inverter-alarm-codes-complete-list-


# State

CURRENT_STATE

0: Standby / Wait
1: Waiting
2: Checking
3: Normal / Generating (MPPT mode)
4: Fault
5: Permanent Fault
6: Upgrading 

# Grid Code Work Mode

01: Volt-Watt – Adjusts active power output based on voltage levels.
02: Volt-Var – Controls reactive power in response to voltage changes.
03: Fixed Power Factor – Maintains a constant power factor regardless of grid conditions.
04: Fixed Reactive Power – Delivers a constant amount of reactive power.
05: Active Power–Power Factor – Manages active power in coordination with power factor.
0C: Active Power–Reactive Power (USA only) – Customized mode for U.S. grid requirements.
