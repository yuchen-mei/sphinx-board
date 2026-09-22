# References

Exact component datasheet links are also recorded in the [parts catalog](../schematic/bom/parts_catalog.json).

| Document | Application |
|---|---|
| [TI TPS546B24A](https://www.ti.com/lit/ds/symlink/tps546b24a.pdf) | Core regulator, ADRSEL, compensation, protection, and layout |
| [TI TPS6213x](https://www.ti.com/lit/ds/symlink/tps62130.pdf) | Fixed 1.8 V regulator and VIN-relative EN/SS/TR ratings |
| [TI TPS25947](https://www.ti.com/lit/ds/symlink/tps25947.pdf) | Input eFuse, thresholds, fault behavior, and ILM routing |
| [TI TLV3011](https://www.ti.com/lit/ds/symlink/tlv3011.pdf) | Comparator and reference specifications |
| [TI TLV755P](https://www.ti.com/lit/ds/symlink/tlv755p.pdf) | U901 independent 3.3 V LDO, enable, and effective-capacitance requirements |
| [TI ISO1640](https://www.ti.com/lit/ds/symlink/iso1640.pdf) | U902 board-side/Pico-side I2C separation, power-down behavior, logic levels, and bus loading |
| [Yageo RT-series V17](https://yageogroup.com/content/datasheet/asset/file/PYU-RT_1-TO-0-01_ROHS_L) | R1002 exact12.6k ordering code,0.1% tolerance,25ppm/C and0603 ratings |
| [TI TCA9535 Rev. F](https://www.ti.com/lit/ds/symlink/tca9535.pdf) | U903 retained outputs, power-on defaults, direction registers, address straps, and junction-temperature-dependent SDA current |
| [Samsung CL21B475KOFNNNE](https://product.samsungsem.com/mlcc/CL21B475KOFNNN.do) | C202/C901/C902 specifications and NRND manufacturer status checked 2026-09-22 |
| [TI ADS1115](https://www.ti.com/lit/ds/symlink/ads1115.pdf) | U904 temperature telemetry, conversion range, and analog input loading |
| [TI TMP302](https://www.ti.com/lit/gpn/TMP302) | U1001 B-version 75°C straps, hysteresis, accuracy, startup time, and DRL footprint |
| [TI TPS3808](https://www.ti.com/lit/ds/symlink/tps3808.pdf) | U502 control supervisor and R1001-selected 300 ms nominal startup holdoff |
| [TI SN74LVC1G74](https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf) | DCU latch pinout and asynchronous clear |
| [Diodes 74LVC08A](https://www.diodes.com/datasheet/download/74LVC08A.pdf) | U504 quad AND, TSSOP-14 pinout, output drive, and power-off leakage |
| [TI INA226](https://www.ti.com/lit/ds/symlink/ina226.pdf) | Rail telemetry and conversion timing |
| [Diodes DMN62D2UQ](https://www.diodes.com/assets/Datasheets/DMN62D2UQ.pdf) | I/O enable, retained explicit-reset, and hardware-clear pull-down MOSFETs |
| [Toshiba TLP293](https://toshiba.semicon-storage.com/info/docget.jsp?did=14419&prodName=TLP293) | Remote-reset optocoupler and GB selection |
| [3M 280-5205-01 drawing](https://datasheet.octopart.com/280-5205-01-3M-datasheet-21189636.pdf) | QFN80 socket dimensions and footprint |
| [TSMC 2020 Annual Report, p. 14](https://investor.tsmc.com/static/annualReports/2020/english/ebook/files/basic-html/page14.html) | N7 automotive foundation-IP qualification context |

The 3M drawing does not specify a contact-current rating. No numerical socket current rating is assigned here.

The TSMC report describes qualification of N7 automotive foundation IP. It does not specify the junction-temperature limit of this ASIC. This project therefore assigns no junction-temperature rating from that process-level statement.

Experiment inputs are defined in [REQUIREMENTS.md](REQUIREMENTS.md): 0.75 V nominal Core, fixed 1.8 V I/O, approximately 5 W active core power, empirical boost operation around 1.0 V, explicit active-high reset with a running clock, asynchronous reset release, and no specified inter-rail sequence constraint. Functionality runs one kernel; power uses a large back-to-back loop followed by steady averaged readings. Ordinary PG/undervoltage observations are diagnostic and do not automatically reset or stop the experiment. These inputs do not constitute manufacturer absolute-maximum ratings.

The [autonomous power contract](AUTONOMOUS_POWER.md) specifies how these parts are used together. Datasheet state retention and fault behavior do not prove assembled-board behavior during partial supply collapse, input transients, or thermal gradients. Those conditions require the [verification plan](VALIDATION.md).
