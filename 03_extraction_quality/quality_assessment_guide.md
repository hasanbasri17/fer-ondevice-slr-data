# Quality assessment guide

Each primary study is scored on six criteria: Yes = 1, Partly = 0.5, No = 0, for a maximum of 6. Following Kitchenham, the scores weight the strength of evidence during synthesis and are not used to exclude studies. A study scoring below 3 is flagged as low quality; none of the 54 studies fell below this threshold.

| Code | Question | Yes (1) | Partly (0.5) | No (0) |
|---|---|---|---|---|
| QA1 | Are the aim and the deployment context clearly stated? | Aim and target context/device are both stated | Aim stated, context vague | Neither is clear |
| QA2 | Is the lightweight method or architecture described in enough detail to replicate? | Architecture, training setup, and compression steps are given | Main components given, key details missing | Insufficient to replicate |
| QA3 | Are efficiency metrics (latency, FPS, parameters, FLOPs, size, power) reported quantitatively? | At least one metric measured on the target device with numbers | Only model-level metrics (parameters/FLOPs) or partial numbers | Only qualitative claims |
| QA4 | Is the model tested on real hardware (smartphone, edge board, accelerator)? | Measured on the named physical device | Deployed on a device, but measurements are incomplete or the device is unspecified | Not tested on real hardware |
| QA5 | Is recognition performance reported on a public dataset or on real-world data? | Public benchmark or real-user data with a clear protocol | Custom or small dataset, or an unclear protocol | No recognition performance reported |
| QA6 | Are privacy, server/network load, or limitations discussed? | Discussed explicitly, ideally with evidence | Mentioned briefly | Not discussed |

Scores were assigned from the full text where it was accessible (45 studies) and from the abstract otherwise (9 studies, marked `abstrak` in `Extraction_source`).
