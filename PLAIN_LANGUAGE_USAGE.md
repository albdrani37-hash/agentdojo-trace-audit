# Plain-language usage guide

This package checks whether one exact collection of AgentDojo run files can be turned into the same denominators, result cells, and claim links every time.

1. Obtain the exact AgentDojo source archive lawfully and keep it local.
2. Run `./run_all SOURCE_ARCHIVE WORKDIR`.
3. Run `./verify_all WORKDIR`.
4. Read `WORKDIR/reconstruction_report.md` and the JSON reports.

If the source is missing, has different bytes, or belongs to another version, the program stops and explains why. It does not download data, contact GitHub, call a model, or send files. Success applies only to the frozen AgentDojo v1.2.1 corpus and does not prove general benchmark correctness, real-world safety, or external replication.
