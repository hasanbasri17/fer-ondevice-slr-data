# Review protocol summary

## Research questions

| RQ | Question |
|---|---|
| RQ1 | Which model architectures and efficiency techniques are used for lightweight or on-device FER? |
| RQ2 | What real-time performance (latency, FPS, size, power) is reported on mobile/edge devices, and at what accuracy cost? |
| RQ3 | How does the inference location (on-device, edge, fog, cloud) affect server load, network demand, and privacy? |
| RQ4 | In which domains is lightweight FER applied, and to what extent in education and usability evaluation? |
| RQ5 | What research gaps and challenges remain? |

## Database search (ScienceDirect, 14 November 2026)

Fields: title, abstract, keywords. Filters: 2021–2026, research articles. ScienceDirect allows at most eight Boolean operators per field, so the query was split into four complementary strings.

| ID | String | Hits |
|---|---|---|
| S1 | ("facial expression recognition" OR "emotion recognition") AND (mobile OR smartphone OR edge) AND (lightweight OR "real-time") | 38 |
| S2 | ("on-device" OR "edge computing" OR "edge AI" OR cloud) AND ("facial expression" OR "emotion recognition") AND (latency OR bandwidth OR privacy) | 30 |
| S3 | ("facial expression" OR "emotion recognition") AND ("e-learning" OR "online learning" OR usability OR "user experience") AND (mobile OR smartphone OR webcam) | 10 |
| S4 | ("facial expression" OR "facial emotion") AND (quantization OR "knowledge distillation" OR pruning OR MobileNet OR TFLite) | 24 |

S2 was piloted first. Its initial version used the generic terms *emotion* and *affective*, which returned hundreds of task-offloading papers, so the terms were narrowed.

## Snowballing (OpenAlex, 15–18 November 2026)

Backward (referenced works) and forward (citing works) snowballing followed Wohlin (2014) and was iterated until an iteration produced no new studies. Each candidate was automatically filtered by year (2021–2026), type (journal article), language (English), and the presence of FER terms plus efficiency/device terms. Candidates that passed were screened on title and abstract and then judged against the amended IC3, using the full text when it was accessible.

## Eligibility criteria

Inclusion (all required):
- **IC1**: primary study; peer-reviewed English-language journal article published 2021–2026.
- **IC2**: proposes or evaluates expression/emotion recognition from facial images, including multimodal systems in which the face is one modality.
- **IC3 (amended)**: device-level evidence. Either (a) performance is measured on a target mobile, edge, or embedded device, or (b) the system is evaluated at a specific processing location (on-device, edge, fog/MEC, or edge–cloud).

Exclusion:
- **EC1**: non-RGB-face modality (e.g., EEG, speech, physiological signals, thermal images, depth/ToF or capacitive sensors, text).
- **EC2**: no efficiency or on-device deployment aspect.
- **EC3**: not a technical contribution to facial emotion recognition (e.g., FER used only as a measurement tool, or another topic matched by the keywords).

## Protocol amendment (18 November 2026)

The original IC3 required only an explicit treatment of computational efficiency. Full-text reading showed that many studies called their models "lightweight" or "real-time" but measured them only on PCs, server GPUs, or Google Colab. IC3 was therefore tightened to require device-level evidence and was applied uniformly to database and snowballing studies. This removed 11 database studies. All excluded studies remain listed with their reasons.
