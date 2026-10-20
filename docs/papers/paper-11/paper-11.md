# Trust-Aware Federated Learning for Privacy-Preserving IoT Intrusion Detection

## Full manuscript text

### PDF page 1

[View original page](assets/page-001.png)

```text
Academic Editor: Arkaitz Zubiaga
Received: 3 August 2026
Revised: 19 September 2026
Accepted: 25 September 2026
Published: 9 October 2026
Copyright: © 2026 by the authors.
Licensee MDPI, Basel, Switzerland.
This article is an open access article
distributed under the terms and
conditions of the Creative Commons
Attribution (CC BY) license.
Article
Trust-Aware Federated Learning for Privacy-Preserving IoT
Intrusion Detection
Santosh Kumar Banbhrani 1,2,*
, Chen Wei 1 and Muhammad Asad 3,*
1
School of Electrical Engineering, Shaoyang University, Shaoyang 422000, China; 2569@hnsyu.edu.cn
2
Department of Information and Computing, University of Sufism and Modern Science,
Bhit Shah 70140, Sindh, Pakistan
3
Faculty of Science and Engineering, University of Plymouth, Plymouth PL4 8AA, UK
*
Correspondence: santosh.kumar@hnsyu.edu.cn (S.K.B.); muhammad.asad@plymouth.ac.uk (M.A.)
Abstract
The rapid growth of Internet of Things (IoT) networks has increased the need for intrusion
detection mechanisms that provide accurate threat detection while preserving privacy,
resisting malicious clients, and limiting communication overhead. Existing Federated
Learning (FL)-based intrusion detection systems (IDS) remain challenged by heterogeneous
non-IID client data, exposure of model updates, adversarial client participation, and fre-
quent model transmission. To address these limitations, this paper proposes FLZT-IDS (Fed-
erated Learning with Zero-Trust for Intrusion Detection in IoT). The framework employs
gradient-deviation monitoring to mitigate the effects of heterogeneous client updates, while
Graph Neural Networks (GNN) and an Attention-based BiLSTM capture relational and
temporal attack patterns, respectively. Secure Aggregation with Local Differential Privacy
(SALDP) protects transmitted model updates, whereas dynamic trust-based client filtering
limits the contribution of potentially malicious participants. An adaptive communication
mechanism transmits local updates only when the model change exceeds a predefined
threshold, thereby reducing unnecessary communication. Experiments on CICIDS2017 and
Edge-IIoTset show that FLZT-IDS achieves 97.8% and 96.2% accuracy, respectively. Com-
pared with FL-IDS, the adaptive communication and trust-filtering mechanisms reduce
cumulative communication overhead by more than 30% after 100 communication rounds.
Under model-poisoning experiments with 30% malicious clients, FLZT-IDS maintains
accuracies of 89.3% on CICIDS2017 and 87.1% on Edge-IIoTset, demonstrating improved
robustness under the evaluated adversarial setting.
Keywords: federated learning; Zero Trust security; intrusion detection; privacy-preserving
IoT; threat detection
1. Introduction
The rapid proliferation of the Internet of Things (IoT) has transformed modern digital
ecosystems by enabling seamless connectivity across diverse domains such as smart cities,
healthcare, industrial automation, and transportation [1]. With billions of IoT devices
deployed globally, these interconnected systems generate vast amounts of sensitive data
and require real-time communication. However, the expansion of IoT infrastructure has
also introduced significant cybersecurity risks, making these networks prime targets for
malicious actors. Threats such as Distributed Denial of Service (DDoS) attacks, Man-in-the-
Middle (MITM) exploits, malware infections, and unauthorized access compromise not
only data integrity but also the reliability of critical services [2].
Electronics 2026, 15, 4584
https://doi.org/10.3390/electronics15204584
```

### PDF page 2

[View original page](assets/page-002.png)

```text
Electronics 2026, 15, 4584
2 of 27
Intrusion Detection Systems (IDS) have emerged as a key defense mechanism to
mitigate cybersecurity risks in IoT networks. Traditional IDS models rely on centralized
architectures, where data collected from edge devices is transmitted to a central server for
analysis [3]. However, this centralized approach presents multiple challenges, including
scalability issues, single points of failure, and heightened privacy risks. The massive
volume of IoT-generated data places a significant burden on network bandwidth, while
central data repositories become attractive targets for cyber adversaries.
Machine learning-based IDS solutions have gained traction due to their ability to
identify complex attack patterns [4]. However, conventional machine learning approaches
require access to extensive labeled datasets, often collected and stored in centralized reposi-
tories. This raises privacy concerns, as raw data must be transmitted to third-party servers
for model training. Additionally, centralized models are vulnerable to adversarial attacks,
where manipulated training data can deceive the system into misclassifying threats [5].
The lack of robust security frameworks within traditional IDS models exacerbates these
challenges, necessitating a paradigm shift toward decentralized and privacy-preserving
intrusion detection mechanisms.
Federated Learning (FL) has emerged as a promising approach to addressing these
concerns by enabling collaborative model training across multiple devices without shar-
ing raw data. In FL, local models are trained on edge devices, and only model updates
(e.g., gradients or parameters) are shared with a central server, thereby preserving data
privacy. Despite its advantages, FL-based IDS solutions face several challenges, including
non-IID data distributions, high communication overhead, vulnerability to model poi-
soning attacks, and lack of trust assurance [6]. The inherent nature of FL assumes that
all participating devices contribute honestly, yet adversarial participants can compromise
global model integrity through poisoning attacks. Additionally, securing communication
during federated updates remains a critical challenge.
From a methodological perspective, anomaly and fault detection problems have been
addressed through different learning paradigms, including supervised deep learning, few-
shot and cross-modal representation learning, and distributed federated learning. Recent
approaches demonstrate the value of specialized learning paradigms for complex anomaly
detection. For example, a study [7] proposed BCLIP-ADer, a few-shot vision–language
anomaly detection framework that combines Bayesian prompt learning with cross-modal
feature refinement to improve generalization to previously unseen anomalies. Similarly,
in [8] the authors developed a meta-learning-based graph convolutional wavelet net-
work that combines multi-scale signal decomposition, graph-based dependency modeling,
and adaptive loss learning for complex dynamic systems. Although these approaches
demonstrate the effectiveness of advanced representation learning in their respective do-
mains, they are designed for centralized task-specific learning and do not address the
combined requirements of privacy-preserving distributed training, malicious-client filter-
ing, and communication-efficient model exchange that arise in federated IoT intrusion
detection. These requirements motivate a learning framework that integrates complemen-
tary relational and temporal representations with privacy, trust, and communication-aware
federated mechanisms.
To further enhance security, the Zero Trust Security Model has gained widespread
adoption, advocating a “never trust, always verify” approach. Unlike traditional security
models that rely on implicit trust within network perimeters, Zero Trust mandates contin-
uous authentication and access verification for all entities, regardless of location or prior
authentication [9]. Integrating Zero Trust principles with FL-based IDS can significantly
improve the security posture of IoT environments by ensuring that only verified updates
contribute to the global model while mitigating adversarial risks.
https://doi.org/10.3390/electronics15204584
```

### PDF page 3

[View original page](assets/page-003.png)

```text
Electronics 2026, 15, 4584
3 of 27
This paper proposes an innovative FL with Zero Trust for Secure and Private Intrusion
Detection in IoT (FLZT-IDS) framework, integrating privacy-preserving mechanisms to
address the aforementioned challenges. By leveraging Graph Neural Networks (GNN) for
relational pattern recognition, Attention-based BiLSTM for sequential anomaly detection,
and Secure Aggregation with Local Differential Privacy (SALDP), this approach ensures
robust, scalable, and efficient intrusion detection in IoT networks.
1.1. Research Problem & Objectives
Despite the privacy-preserving benefits of FL, existing FL-based IDS struggle with key
challenges: vulnerability to adversarial attacks, high communication overhead, and limited
adaptability [10]. Traditional IDS models expose sensitive data by relying on centralized
processing, while FL, though decentralized remains susceptible to model inversion and
poisoning attacks [11]. Malicious clients can inject manipulated updates to compromise the
global model, and frequent communication between edge devices and the server strains
bandwidth in large-scale IoT networks [12]. Moreover, many FL-based IDS frameworks
fail to adapt to evolving threats, resulting in high false positive and negative rates.
To overcome these limitations, this research introduces FLZT-IDS: a Zero-Trust-
enabled, Privacy-Preserving FL-based IDS for IoT. The framework integrates GNN for
relational pattern recognition and Attention-based BiLSTM for sequential anomaly detec-
tion [13]. A SALDP mechanism further enhances privacy and robustness. Experimental
results on CICIDS2017 and Edge-IIoTset datasets confirm the superior accuracy, scalability,
and resilience of FLZT-IDS over existing approaches. Table 1 summarizes the abbreviations
and mathematical notations widely used throughout this manuscript.
Table 1. List of Abbreviations and Notations Used in This Paper.
Abbreviation/
Symbol
Definition
Abbreviation/
Symbol
Definition
FL
Federated Learning
IDS
Intrusion Detection System
IoT
Internet of Things
GNN
Graph Neural Network
BiLSTM
Bidirectional Long Short-Term Memory
DP
Differential Privacy
LDP
Local Differential Privacy
SALDP
Secure Aggregation with Local Differen-
tial Privacy
ZTM
Zero Trust Model
FPR
False Positive Rate
ACC
Accuracy
P
Precision
R
Recall
F1
F1-Score
FedAvg
Federated Averaging
FedGAT
Federated Graph Attention Network
Fed-ANIDS
Federated Anomaly-based Intrusion De-
tection System
FLZT-IDS
Federated Learning with Zero Trust for
Intrusion Detection in IoT
SMOTE
Synthetic Minority Over-sampling Tech-
nique
HE
Homomorphic Encryption
CCPA
California Consumer Privacy Act
GDPR
General Data Protection Regulation
|D|
Total number of training samples
δmax
Maximum allowable gradient-deviation
threshold
et
Unnormalized temporal-attention score
I
Identity matrix in the Gaussian-noise co-
variance
y
Predicted binary class label (Benign or
Attack)
⊕
Homomorphic addition of encrypted
updates
ε
Differential-privacy budget
εcomm
Communication-update threshold
1.2. Contributions
This paper makes the following key contributions to IoT security research:
https://doi.org/10.3390/electronics15204584
```

### PDF page 4

[View original page](assets/page-004.png)

```text
Electronics 2026, 15, 4584
4 of 27
•
We integrate GNN with FL to capture relational dependencies in network traffic,
enhancing intrusion detection accuracy for complex cyber threats.
•
We employ an Attention-based BiLSTM model to detect sequential attack patterns,
improving adaptability to evolving threats and reducing false positive rates.
•
We implement SALDP to ensure privacy-preserving model updates, mitigating risks
from adversarial model poisoning attacks.
•
We evaluate the proposed framework using CICIDS2017 and Edge-IIoTset datasets,
demonstrating superior detection performance, privacy protection, and scalability
compared to existing FL-based IDS solutions.
1.3. Paper Organization
The paper is structured as follows. Section 2 reviews literature review on IDS frame-
works, FL in cybersecurity, and Zero Trust security. Section 3 presents the proposed
FL-ZT-IDS methodology, integrating GNN, Attention-based BiLSTM, and SALDP. Section 4
outlines the experimental setup, including datasets, model training, and evaluation metrics.
Section 5 analyzes results and compares FL-ZT-IDS with existing approaches. Section 6 dis-
cusses key findings, limitations, and future research directions. Finally, Section 7 concludes
the paper.
2. Literature Review
This section reviews intrusion detection in IoT, covering traditional IDS approaches,
FL-based IDS, and Zero Trust security. It also examines the limitations of centralized IDS
and the need for privacy-preserving, adaptive security solutions.
2.1. Traditional IDS Approaches for IoT Security
IDS play a critical role in securing IoT networks by identifying unauthorized activities
and cyber threats. Traditional IDS approaches are broadly classified into signature-based
detection and anomaly-based detection [14]. Signature-based IDS rely on predefined attack
signatures, making them effective against known threats but incapable of detecting novel
cyberattacks [15]. In contrast, anomaly-based IDS monitor network behavior and flag
deviations as potential threats, enabling the detection of previously unseen attacks but
often resulting in higher false positive rates [16]. These conventional IDS models face
limitations in adapting to evolving attack patterns, handling large-scale IoT networks, and
maintaining real-time detection accuracy.
2.1.1. Signature-Based vs. Anomaly-Based Detection Methods
Signature-based IDS compare incoming network traffic against a database of known at-
tack patterns. This approach is widely used in IDS tools such as Snort and Suricata, offering
high detection accuracy for previously identified threats with minimal false positives [17].
However, the reliance on predefined signatures makes these systems ineffective against
zero-day exploits and adversarial attacks [18]. To address this limitation, anomaly-based
IDS employ machine learning, statistical models, and deep learning techniques to establish
baselines of normal network behavior and detect deviations [19]. While anomaly-based
IDS can identify unknown attacks, they suffer from high false positive rates and require
frequent model retraining to adapt to dynamic IoT environments.
2.1.2. Challenges in Centralized Intrusion Detection Systems
Most traditional IDS frameworks operate in a centralized manner, where IoT devices
transmit network logs to a central server for analysis. While this architecture facilitates
large-scale monitoring, it introduces scalability, latency, and privacy challenges [20]. High
network traffic from multiple IoT devices leads to computational bottlenecks, limiting real-
https://doi.org/10.3390/electronics15204584
```

### PDF page 5

[View original page](assets/page-005.png)

```text
Electronics 2026, 15, 4584
5 of 27
time detection capabilities. Moreover, single points of failure in centralized IDS make them
vulnerable to distributed denial-of-service (DDoS) attacks and adversarial manipulations,
reducing their effectiveness in securing IoT networks [21]. These limitations highlight the
need for decentralized and privacy-preserving IDS solutions, such as FL-based IDS, which
can enhance security without compromising efficiency.
2.2. Federated Learning for Intrusion Detection
FL has emerged as an effective approach for intrusion detection in IoT by enabling
collaborative model training without exposing raw data, thus preserving privacy and
reducing communication overhead. Unlike centralized IDS, where data is transmitted
to a central server, FL ensures that only model updates are shared, reducing the risk of
data breaches. This decentralized learning paradigm is particularly beneficial for IoT net-
works, where data is generated across heterogeneous devices with varying computational
capabilities [20].
Several FL-based IDS frameworks have demonstrated improved detection accuracy
while maintaining privacy. In [22] an FL-based IDS for IoT achieves efficient anomaly
detection without data centralization. However, FL-based IDS faces challenges, including
non-IID data distributions, which can degrade global model performance, and model
poisoning attacks, where adversarial nodes inject malicious updates to compromise the
system [23]. Additionally, FL introduces high communication costs, making real-time
intrusion detection challenging in resource-constrained IoT environments. Addressing
these issues requires optimized aggregation mechanisms, adversarial defense techniques,
and communication-efficient training strategies to enhance the robustness and scalability
of FL-based IDS [24].
2.3. Zero-Trust Security Model in IoT
The Zero-Trust Security Model (ZTSM) has gained significant attention in securing
IoT environments by enforcing strict access controls and eliminating implicit trust in
devices or users [25]. Unlike traditional perimeter-based security approaches, Zero-Trust
requires continuous authentication, authorization, and policy enforcement to mitigate
unauthorized access risks. Recent studies [26,27] have explored its integration into IoT
networks, emphasizing its role in protecting against evolving cyber threats such as man-
in-the-middle attacks, privilege escalation, and unauthorized device access. However,
applying Zero-Trust principles to IoT remains challenging due to the heterogeneous nature
of IoT devices, constrained computational resources, and the dynamic nature of network
interactions [28].
Incorporating Zero-Trust with FL-IDS presents a promising avenue for enhancing
security without compromising privacy. Studies [29,30] have demonstrated that Zero-Trust-
driven FL-IDS improves intrusion detection accuracy by ensuring that only verified and
authenticated devices participate in federated training. Additionally, secure aggregation
techniques such as homomorphic encryption and differential privacy can further mitigate
model poisoning risks while maintaining the decentralized advantage of FL. Despite these
advancements, ensuring scalability and optimizing computational overhead remain open
research challenges that require further investigation in large-scale IoT deployments.
2.4. Privacy-Preserving Techniques in FL-Based IDS
Privacy preservation is a critical concern in FL-IDS, as sensitive data remains dis-
tributed across IoT devices. Unlike centralized IDS, where raw data is transferred to a
central server, FL ensures that only model updates are shared, reducing exposure to data
breaches [31]. However, privacy threats such as model inversion attacks, membership
inference attacks, and data reconstruction vulnerabilities still pose significant risks [32]. To
https://doi.org/10.3390/electronics15204584
```

### PDF page 6

[View original page](assets/page-006.png)

```text
Electronics 2026, 15, 4584
6 of 27
address these issues, various privacy-preserving techniques, including differential privacy
(DP), homomorphic encryption (HE), and secure multi-party computation (SMPC), have
been integrated into FL-based IDS frameworks [12]. DP adds statistical noise to model
updates, ensuring that individual device contributions remain indistinguishable, while
HE allows computations on encrypted data, preventing attackers from extracting sensitive
information during aggregation [33].
Secure aggregation protocols further enhance privacy by masking individual model
updates before they reach the central server, preventing malicious entities from reconstruct-
ing private data [34]. Recent research [35,36] has explored combining Zero-Trust principles
with privacy-preserving FL-IDS to ensure that only authenticated nodes contribute to the
training process, reducing risks from adversarial attacks. Despite these advancements,
achieving an optimal balance between privacy, computational efficiency, and model accu-
racy remains an ongoing challenge, particularly in resource-constrained IoT environments
where cryptographic operations introduce additional overhead. Future research must focus
on lightweight encryption techniques and adaptive privacy mechanisms to enhance the
deployment feasibility of privacy-preserving FL-based IDS at scale.
2.5. Learning Paradigms and Related Approaches
Existing anomaly and intrusion detection studies can also be distinguished according
to their underlying learning paradigms. Supervised deep learning methods learn dis-
criminative representations from labeled training data and can achieve high predictive
performance when representative labels are available [37]. Recent graph-based approaches
extend this paradigm by explicitly modeling structural dependencies. For example, Ref. [8]
proposed a meta-learning-based graph convolutional wavelet network that combines multi-
scale wavelet decomposition with graph convolution and adaptive loss learning to capture
nonlinear relationships among multiple system variables. Although such approaches
demonstrate the effectiveness of graph-based relational modeling, they assume centralized
access to training data and are not designed to address privacy or malicious-client behavior
in distributed learning environments.
Alternative paradigms have been developed for settings in which abnormal samples
are scarce. Ref. [7] proposed BCLIP-ADer, a few-shot anomaly detection approach based
on Bayesian prompt learning and contrastive vision–language representations. The method
improves generalization to unseen anomaly types by learning diverse text prompts and
refining cross-modal representations. Such few-shot and cross-modal approaches address
limited anomaly examples and representation generalization; however, their objectives
differ from federated intrusion detection, where model updates originate from distributed
and potentially untrusted clients [38].
Federated learning provides a complementary paradigm by allowing multiple clients
to collaboratively train a model without directly sharing raw data [39]. Existing FL-based
IDS methods address different subsets of this problem. FL-IDS [40] employs federated
training with a conventional neural-network-based detector, while FedGAT [41] introduces
graph attention to capture relational dependencies among network traffic instances. Fed-
ANIDS focuses on federated anomaly detection using autoencoder-based representations.
These approaches improve decentralization or attack representation, but they do not
jointly incorporate trust-aware client participation, local differential privacy with secure
aggregation, and communication-triggered model transmission.
Therefore, the distinction of FLZT-IDS is not the individual use of GNN, BiLSTM,
federated learning, or privacy mechanisms in isolation. Rather, the proposed framework in-
tegrates complementary relational and temporal modeling with privacy-preserving model-
update transmission, dynamic trust-based client filtering, and adaptive communication
https://doi.org/10.3390/electronics15204584
```

### PDF page 7

[View original page](assets/page-007.png)

```text
Electronics 2026, 15, 4584
7 of 27
within a single federated IDS pipeline. Table 2 summarizes the methodological differ-
ences between representative approaches and clarifies the specific integration addressed
by FLZT-IDS.
Table 2. Comparison of representative learning paradigms and their relationship to FLZT-IDS.
Method
Learning Paradigm
Primary Modeling Focus
Privacy-
Aware FL
Trust/ Ro-
bustness
Adaptive
Comm.
BCLIP-ADer
Few-shot vision–language
learning
Cross-modal anomaly representation
and unseen-anomaly generalization
No
No
No
Meta-learning graph
convolutional wavelet
network
Graph-based meta-learning
Multi-scale dynamic and relational
modeling
No
No
No
FL-IDS
Federated learning
Distributed neural-network-based
intrusion detection
Partial
No
No
FedGAT
Federated graph learning
Relational dependencies in network
traffic
Partial
No
No
Fed-ANIDS
Federated anomaly detection
Autoencoder-based anomaly
representation
Partial
No
No
FLZT-IDS
Federated hybrid learning
Relational and temporal intrusion
modeling
Yes
Yes
Yes
2.6. Gaps in Existing Work & Research Direction
Despite significant advancements in FL, Zero-Trust Security, and IDS for IoT, several
research gaps remain unaddressed. Existing FL-based IDS frameworks struggle with
challenges such as high communication overhead, vulnerability to adversarial attacks,
and handling non-IID data distributions [29,42]. Similarly, Zero-Trust Security models
in IoT require extensive computational resources for continuous verification, making
them less feasible for resource-constrained edge devices [43]. As summarized in Table 2,
existing approaches address important but largely complementary aspects of anomaly
and intrusion detection, including graph-based representation learning, few-shot anomaly
generalization, federated training, and privacy preservation. Among the representative
methods reviewed, none jointly combines relational and temporal intrusion modeling,
privacy-preserving federated update transmission, dynamic trust-based client filtering, and
adaptive communication. FLZT-IDS is designed to address this integration gap within a
unified federated IoT intrusion-detection pipeline.
To address these challenges, future research should focus on lightweight privacy-
preserving techniques, robust aggregation mechanisms for secure FL, and adaptive in-
trusion detection models that can evolve with emerging threats. Additionally, hybrid
approaches integrating blockchain with FL and Zero-Trust could further enhance trust
verification and data integrity in decentralized environments.
3. Proposed Methodology: FLZT-IDS
3.1. Overview of the Proposed Framework
The proposed FLZT-IDS integrates FL, Zero-Trust Security, and Privacy-Preserving
mechanisms to enhance the security and efficiency of IoT-based intrusion detection. Unlike
traditional IDS, which rely on centralized data collection, FLZT-IDS ensures decentralized
training across IoT devices, reducing privacy risks while enabling real-time attack detec-
tion. As shown in Figure 1, the framework enforces strict access policies using Zero-Trust
principles, ensuring that only authenticated and verified nodes participate in the FL pro-
cess. Furthermore, privacy-preserving techniques, such as differential privacy and secure
aggregation, safeguard model updates from adversarial threats and data inference attacks.
https://doi.org/10.3390/electronics15204584
```

### PDF page 8

[View original page](assets/page-008.png)

```text
Electronics 2026, 15, 4584
8 of 27
Figure 1. System overview of FLZT-IDS: IoT clients train local models on private data and are
filtered by a Zero-Trust Gate based on trust scores. Trusted clients apply a multi-modal deep model
(GNN + BiLSTM), followed by privacy-preserving transmission using SALDP. The central server
aggregates these updates to form a global model Wt+1, which is broadcast back to clients.
Let D = {D1, D2, . . . , DN} represent the distributed datasets across N IoT devices.
Each device i trains a local model wi on its dataset Di, and instead of sharing raw data, only
model updates ∆wi are transmitted to the central server for aggregation. The global model
update at round t follows:
wt+1 =
N
∑
i=1
|Di|
|D| wt
i
(1)
where |Di| is the number of training samples at device i, ensuring weighted aggregation
proportional to dataset sizes.
To incorporate Zero-Trust Security, each participating IoT device must satisfy the
server-side trust-verification criterion before contributing to the FL process. This is achieved
by assigning each device a trust score τi, computed as:
τi = αRi + βCi + γAi
(2)
where Ri, Ci, and Ai are normalized to the range [0, 1] and are computed by the server-
side trust monitor rather than obtained directly from CICIDS2017 or Edge-IIoTset. In
the experiments, the weighting coefficients are set to α = 0.4, β = 0.3, and γ = 0.3. Ri
represents the proportion of successful client participations within a sliding window of the
previous W = 5 communication rounds, while Ci represents the proportion of protocol-
compliance checks successfully satisfied during the same window. Ai is derived from
the historical deviation of the client’s model updates from the global training behavior,
with smaller deviations producing higher confidence scores. All three components are
computed from server-observed training and communication behavior and do not use the
ground-truth attack labels of CICIDS2017 or Edge-IIoTset. Therefore, the trust calculation
does not introduce label leakage.
The trust evidence is updated after each communication round using the most recent
five-round window. For cold-start clients, an initial trust score of τ0
i = 0.7 is assigned,
after which the score is replaced by the observed evidence-based value. Since the trust
evidence is computed by the server rather than self-reported by the client, a malicious
client cannot directly forge Ri, Ci, or Ai; abnormal model-update behavior instead reduces
its anomaly-confidence and compliance scores. A client is accepted for aggregation only
when τi > τthreshold.
A device is allowed to participate only if τi > τthreshold, ensuring only trustworthy
nodes contribute to the model.
For privacy preservation, we integrate differential privacy by adding noise N (0, σ2)
to each local update:
˜wi = wi + N (0, σ2)
(3)
where σ controls the privacy–accuracy tradeoff. Secure aggregation techniques ensure that
the server cannot reconstruct individual updates, preserving confidentiality.
https://doi.org/10.3390/electronics15204584
```

### PDF page 9

[View original page](assets/page-009.png)

```text
Electronics 2026, 15, 4584
9 of 27
The combination of FL, Zero-Trust Security, and Privacy-Preserving Mechanisms
ensures that FLZT-IDS provides robust, scalable, and attack-resilient intrusion detection
in IoT environments. The subsequent sections elaborate on the detailed methodology for
model training, security enforcement, and privacy-preserving techniques.
3.2. Federated Learning-Based IDS for IoT
The FLZT-IDS framework leverages FL to develop an IDS that enables decentralized
model training while preserving privacy. Unlike centralized IDS, FL ensures that each IoT
device trains a local model on its data and transmits only model updates to the central
server. This reduces privacy risks and enhances scalability. However, FL-based IDS faces
key challenges, including non-IID data distribution, susceptibility to adversarial attacks,
and communication overhead, which impact model performance.
One of the critical challenges in FL is data heterogeneity, where IoT devices generate
non-IID data, leading to biased global models [44]. To quantify this divergence, a device-
specific gradient deviation factor is introduced:
δi = ||∇Li(wt
i) −∇L(wt)||2
(4)
where ∇Li(wt
i) is the local gradient at device i, and ∇L(wt) is the aggregated gradient. If
δi > δmax, additional local training is triggered to align the model with the global objective.
To counter adversarial updates, Zero-Trust Security mechanisms verify the integrity of
model updates before aggregation. Each device’s update is evaluated using its trust score
τi (Equation (2)). Additionally, SALDP protects updates from reconstruction attacks by
applying encryption and noise injection, as formulated in Equation (3).
To further optimize model communication efficiency, an adaptive update mechanism
is introduced, where only significant updates are transmitted. The communication round
is triggered when the model’s local change ∆wi surpasses a predefined threshold:
||∆wi|| > ϵ
(5)
where ϵ controls the frequency of updates, reducing unnecessary transmissions.
By integrating gradient alignment, Zero-Trust verification, secure aggregation, and
adaptive communication, FLZT-IDS ensures efficient, scalable, and attack-resilient intrusion
detection for IoT networks.
3.3. GNN for Relational Pattern Recognition
Traditional intrusion detection models often fail to capture the complex interdependen-
cies between network attacks, as they treat threats as independent instances [45]. However,
in IoT environments, attacks often exhibit structured relationships, such as botnet infections
or coordinated multi-stage intrusions. GNN provide a powerful solution by modeling
these relationships in a graph structure, where nodes represent network traffic instances
and edges capture behavioral similarities or dependencies.
In the implementation, graphs are constructed independently within each client and
within each data partition after the train–validation–test split. Each node represents one
network-flow instance, and each local mini-batch contains up to 128 nodes. For every node,
edges are formed with its k = 5 nearest neighbors according to cosine similarity in the
normalized feature space. Self-loops are included, and the adjacency matrix is normalized
as ˆA = D−1/2(A + I)D−1/2. No edges are created across different clients or between
training, validation, and test partitions, thereby preventing test samples from influencing
graph-based training.
https://doi.org/10.3390/electronics15204584
```

### PDF page 10

[View original page](assets/page-010.png)

```text
Electronics 2026, 15, 4584
10 of 27
In FLZT-IDS, an attack graph G = (V, E) is constructed, where V represents network
events and E encodes relationships between them. The adjacency matrix A ∈R|V|×|V|
defines connections between nodes based on shared features or temporal correlations.
The implemented graph encoder uses a single normalized GCN layer with ReLU activa-
tion. The resulting graph representation is subsequently concatenated with the temporal
representation produced by the Attention-based BiLSTM, as illustrated in Figure 2.
Figure 2. Deep learning architecture in FLZT-IDS. The GCN branch processes graph-structured
network-flow data and produces the graph representation hGNN, while the Attention-based BiLSTM
processes temporal sequences and produces the attention-weighted context vector cBiLSTM. The two
representations are concatenated and passed through a 128-unit dense layer with ReLU activation,
dropout (p = 0.5), and a two-unit softmax output layer.
To enhance the representation of network anomalies, a graph attention mechanism
assigns importance scores αij to neighboring nodes, refining information propagation:
αij =
exp
(︁
LeakyReLU
(︁
a⊤[hi∥hj]
)︁)︁
∑k∈N (i) exp
(︁
LeakyReLU
(︁
a⊤[hi∥hk]
)︁)︁
(6)
where hi and hj are feature embeddings of nodes i and j. Symbol a is a trainable attention
vector, and N (i) represents the neighborhood of node i.
The graph encoder produces a graph-level representation hGNN, which is not classified
independently. Instead, hGNN is passed to the feature-fusion stage and combined with the
temporal representation produced by the Attention-based BiLSTM.
By incorporating GNN-based relational learning, FLZT-IDS effectively detects attack
patterns that traditional IDS models overlook, improving detection accuracy and resilience
to sophisticated cyber threats.
3.4. Attention-Based BiLSTM for Sequential Anomaly Detection
Intrusion detection in IoT networks requires analyzing network traffic patterns over
time to detect sequential anomalies, such as slow-propagating malware and coordinated
attacks. Traditional IDS models struggle to capture long-range dependencies in time-series
network data. Bidirectional Long Short-Term Memory (BiLSTM) addresses this limitation
by processing each sequence in both forward and backward directions, thereby capturing
contextual dependencies from preceding and succeeding network events [46]. To further
improve feature representation, an attention mechanism is integrated to emphasize the
time-steps that contribute most strongly to anomaly detection.
https://doi.org/10.3390/electronics15204584
```

### PDF page 11

[View original page](assets/page-011.png)

```text
Electronics 2026, 15, 4584
11 of 27
Given a sequence of network events X = {x1, x2, . . . , xT}, the BiLSTM consists of
forward and backward LSTM units. For each direction d ∈{→, ←}, the input gate, forget
gate, output gate, candidate memory state, cell state, and hidden state are computed as:
id
t = σ
(︂
Wd
i xt + Ud
i hd
t−1 + bd
i
)︂
,
(7)
f d
t = σ
(︂
Wd
f xt + Ud
f hd
t−1 + bd
f
)︂
,
(8)
od
t = σ
(︂
Wd
o xt + Ud
o hd
t−1 + bd
o
)︂
,
(9)
˜cd
t = tanh
(︂
Wd
c xt + Ud
c hd
t−1 + bd
c
)︂
,
(10)
cd
t = f d
t ⊙cd
t−1 + id
t ⊙˜cd
t ,
(11)
hd
t = od
t ⊙tanh
(︂
cd
t
)︂
,
(12)
where id
t , f d
t , and od
t denote the input, forget, and output gates, respectively; ˜cd
t is the
candidate memory state; cd
t is the cell state; and hd
t is the hidden state in direction d. The
matrices Wd
{·} and Ud
{·} are learnable input and recurrent weight matrices, respectively,
while bd
{·} represents the corresponding bias terms. The sigmoid function σ(·) controls the
gating operations, tanh(·) produces the candidate and output activations, and ⊙denotes
element-wise multiplication. The backward LSTM applies the same operations while
processing the sequence in reverse temporal order.
The bidirectional representation at time-step t is obtained by concatenating the forward
and backward hidden states:
ht =
[︂−→
ht ∥←−
ht
]︂
.
(13)
For the experiments, network flows are ordered by their timestamp within each collection
session and converted into sequences of T = 20 consecutive flows. Sequences are generated
using a sliding window with a stride of 10 flows, corresponding to 50% overlap. Win-
dows do not cross session, client, or train–validation–test boundaries; therefore, temporal
sequences used for training contain only local training observations.
To enhance the model’s focus on important time-steps, an attention mechanism is
applied, computing attention scores αt for each hidden state:
αt =
exp(et)
∑T
j=1 exp(ej)
(14)
where
et = v⊤tanh(Whht + bh)
(15)
where Wh and bh are trainable attention parameters and v is the attention vector. The final
context vector c, representing the weighted sum of hidden states, is
c =
T
∑
t=1
αtht
(16)
The attention-weighted context vector cBiLSTM is not classified independently. Instead, it is
concatenated with the graph representation hGNN to form the fused representation:
hfusion = hGNN∥cBiLSTM,
(17)
https://doi.org/10.3390/electronics15204584
```

### PDF page 12

[View original page](assets/page-012.png)

```text
Electronics 2026, 15, 4584
12 of 27
where ∥denotes vector concatenation. The fused representation is then passed through a
128-unit fully connected layer with ReLU activation and dropout with p = 0.5:
h f = Dropout
(︂
ReLU
(︂
Wf hfusion + bf
)︂
, p = 0.5
)︂
.
(18)
The final two-class output logits are computed as
o = Woh f + bo,
(19)
and the probability of output class k is obtained using softmax:
P(y = k | h f ) =
exp(ok)
∑2
j=1 exp(oj)
,
k ∈{1, 2}.
(20)
The two output classes correspond to Benign and Attack.
By combining the graph-based representation with the attention-weighted BiLSTM
representation, FLZT-IDS jointly captures relational and temporal patterns in network
traffic. The fused representation is subsequently used for binary intrusion classification.
The overall DL architecture combining graph-based and sequence-based modeling in
FLZT-IDS is illustrated in Figure 2.
3.5. Secure Aggregation with Local Differential Privacy (SALDP)
While FL enhances privacy by keeping data local, the transmission of model updates
still poses risks of inference attacks and adversarial manipulations. To counter this, FLZT-
IDS employs SALDP, ensuring that model updates remain confidential while preventing
malicious contributions.
3.5.1. Local Differential Privacy for Secure Model Updates
To provide a bounded sensitivity for the Gaussian mechanism, each client update ∆wi
is first clipped using an ℓ2 norm bound C = 1.0:
∆wi =
∆wi
max
(︂
1, ∥∆wi∥2
C
)︂.
(21)
Gaussian noise is then added to the clipped update:
˜︂
∆wi = ∆wi + N
(︂
0, σ2C2I
)︂
,
(22)
where σ denotes the Gaussian noise multiplier. With the clipping norm fixed at C = 1.0,
the ℓ2 sensitivity of each bounded client update is taken as ∆2 = C = 1.0. Unlike pure
ε-differential privacy, the Gaussian mechanism is characterized using (ε, δ)-differential
privacy. For two neighboring updates u and u′, the randomized mechanism M satisfies
Pr[M(u) ∈S] ≤eε Pr[M(u′) ∈S] + δ,
(23)
for any measurable output set S.
In the federated setting, two clients are randomly sampled from the ten available
clients in each communication round, corresponding to a client sampling rate of q = 0.2.
The privacy failure probability is fixed at δ = 10−5. Privacy loss is accumulated over the
complete training process using a Rényi Differential Privacy (RDP) accountant, which
accounts for the sampling rate, Gaussian noise multiplier, and composition across 100 com-
https://doi.org/10.3390/electronics15204584
```

### PDF page 13

[View original page](assets/page-013.png)

```text
Electronics 2026, 15, 4584
13 of 27
munication rounds. The resulting (ε, δ) privacy budgets for the evaluated noise levels are
reported in Section 5.3.
3.5.2. Secure Weighted Aggregation for Privacy-Preserving FL
To prevent the aggregation server from accessing individual client updates, FLZT-IDS
employs secure weighted aggregation based on additive homomorphic encryption. A
common public key pk is made available to participating clients, while the corresponding
private key sk is retained by a separate trusted key holder and is not accessible to the
aggregation server. After applying local differential privacy, each eligible client i encrypts
its weighted perturbed model update as
ci = Encpk(|Di| ˜︁wi),
(24)
where |Di| denotes the number of local training samples and ˜︁wi is the locally perturbed
model update. Let St denote the set of trusted and active clients whose updates satisfy the
communication threshold and are successfully received during communication round t.
Using the additive homomorphic property, the server computes
Ct =
⨁︂
i∈St
ci = Encpk
(︄
∑
i∈St
|Di| ˜︁wi
)︄
,
(25)
without decrypting any individual client update. Only the aggregated ciphertext Ct is sub-
mitted to the trusted key holder for decryption. The resulting aggregate is then normalized
to obtain the global model:
wt+1 = Decsk(Ct)
∑i∈St |Di|.
(26)
This procedure is equivalent to weighted FedAvg over the participating clients while
preserving the confidentiality of individual updates. Client dropout is handled by con-
structing St only from trusted clients whose encrypted updates are successfully received
within the current communication round; therefore, both the encrypted numerator and the
normalization denominator are computed over the same active-client set.
The threat model assumes that the aggregation server and the trusted key holder
do not collude. The aggregation server possesses only the public key and is therefore
permitted to perform homomorphic operations but not to decrypt individual ciphertexts.
The key holder decrypts only the aggregated ciphertext and does not receive individual
client ciphertexts. Consequently, FLZT-IDS does not claim protection against collusion
between the aggregation server and the key holder; supporting such a stronger threat
model would require threshold decryption or a secure multi-party computation protocol.
3.5.3. Robustness Through Trust-Based Client Filtering
FLZT-IDS addresses adversarial client participation before secure aggregation rather
than applying a second aggregation rule after decryption. Each participating client is eval-
uated using the dynamic trust score defined in Equation (2), and clients with τi ≤τthreshold
are excluded from the active aggregation set St. Gradient-deviation monitoring further
identifies abnormal local training behavior before an update is accepted for transmission.
Consequently, only updates from clients that satisfy the trust, gradient-deviation, and com-
munication criteria are included in the secure weighted aggregation procedure described
in Section 3.5.2.
This design separates adversarial filtering from aggregation: trust-based verification
determines which client updates are eligible, while a single secure weighted FedAvg
https://doi.org/10.3390/electronics15204584
```

### PDF page 14

[View original page](assets/page-014.png)

```text
Electronics 2026, 15, 4584
14 of 27
operation combines the accepted updates. No coordinate-wise median or individual-
update decryption is performed at the server.
3.6. Model Training & Communication Rounds
The training process in FLZT-IDS follows a federated and adaptive communication
strategy to balance model convergence and communication efficiency. Each IoT device i
trains a local model wi using its dataset Di, updating parameters via gradient descent:
wt+1
i
= wt
i −η∇Li(wt
i)
(27)
where η is the learning rate.
To reduce communication overhead, updates are transmitted only when the model
change exceeds a threshold ϵcomm:
||wt+1
i
−wt
i|| > ϵcomm
(28)
The accepted client updates are combined using the secure weighted FedAvg proce-
dure described in Section 3.5.2. Trust-based participation and gradient-deviation monitor-
ing are applied before aggregation, while the server operates only on encrypted accepted
updates and does not access individual plaintext model updates. This provides a single
and consistent aggregation procedure across the FLZT-IDS framework. The complete
workflow of the proposed FLZT-IDS framework is summarized in Algorithm 1, and its
visual execution process is illustrated in Figure 3.
Algorithm 1 FLZT-IDS: Federated Learning with Zero-Trust and Secure Aggregation
1: Input: Global model w0, rounds T, devices {1, . . . , N}, thresholds τthreshold, δmax, ϵcomm, privacy
noise scale σ, learning rate η, public key pk
2: Output: Trained global model wT
3: for t = 0 to T −1 do
4:
Randomly sample client set Ct with |Ct| = 2 (q = 0.2)
5:
Initialize active-client set St ←∅
6:
for all device i ∈Ct in parallel do
7:
Compute trust score τi = αRi + βCi + γAi
8:
if τi > τthreshold then
9:
Initialize wt
i ←wt and train local model
10:
Compute gradient deviation δi
11:
if δi > δmax then
12:
Continue local training
13:
end if
14:
if ∥wt+1
i
−wt
i∥> ϵcomm then
15:
Add noise: ˜︁wi = wt+1
i
+ N (0, σ2)
16:
Encrypt weighted update: ci = Encpk(|Di| ˜︁wi)
17:
Add i to St
18:
end if
19:
end if
20:
end for
21:
if St ̸= ∅then
22:
Homomorphically aggregate: Ct = ⨁︁
i∈St ci
23:
Decrypt aggregate: zt = Decsk(Ct)
24:
Update global model: wt+1 = zt
/︁
∑i∈St |Di|
25:
else
26:
wt+1 ←wt
27:
end if
28: end for
29: return wT
https://doi.org/10.3390/electronics15204584
```

### PDF page 15

[View original page](assets/page-015.png)

```text
Electronics 2026, 15, 4584
15 of 27
Figure 3. Execution flow of FLZT-IDS showing the client–server boundary, local graph and se-
quence construction, gradient-deviation screening, communication triggering, privacy perturbation,
encrypted model-update transmission, secure aggregation, aggregate-only decryption, and global-
model update. Plaintext local model updates remain on the client side, while only encrypted
perturbed updates are transmitted to the aggregation server.
4. Experimental Setup
This section outlines the experimental design used to assess the effectiveness of the
proposed FLZT-IDS framework. It includes details on the datasets, implementation envi-
ronment, performance evaluation metrics, and the baseline models used for comparison.
4.1. Datasets Used
To evaluate the intrusion detection capability of FLZT-IDS under both general and in-
dustrial IoT scenarios, we employ two widely used and comprehensive benchmark datasets:
(1) CICIDS2017 [47]: Developed by the Canadian Institute for Cybersecurity, this
dataset comprises a wide range of real-world attack scenarios such as DDoS, brute-force,
botnet, infiltration, and port scanning, collected in a realistic network setting. Each network
flow consists of 80+ statistical and behavioral features extracted using CICFlowMeter,
making it suitable for training deep learning models for intrusion detection.
https://doi.org/10.3390/electronics15204584
```

### PDF page 16

[View original page](assets/page-016.png)

```text
Electronics 2026, 15, 4584
16 of 27
(2) Edge-IIoTset [48]: A recent dataset tailored for Industrial IoT (IIoT) environments,
Edge-IIoTset includes data from smart grid and factory devices, covering both normal and
malicious traffic. It contains various attacks such as ransomware, DDoS, and backdoor
exploits, making it highly relevant for evaluating IDS models in edge-computing-based IoT
environments.
Although both datasets contain multiple attack categories, this study formulates
intrusion detection as a binary classification task by mapping all malicious traffic to the
Attack class and normal traffic to the Benign class. Therefore, the Dense(2) output layer
corresponds to these two classes.
Preprocessing and Data Partitioning: Both datasets undergo a unified preprocess-
ing pipeline. Missing values are imputed or removed, categorical attributes are one-hot
encoded, and numerical features are normalized using Min–Max scaling. To prevent
information leakage, the train, validation, and test partitions are created before oversam-
pling and client allocation. Flows originating from the same collection session are kept
within the same partition so that adjacent or closely related network flows do not appear
simultaneously in the training and test sets. The resulting data are split into 80% train-
ing, 10% validation, and 10% testing subsets using a fixed random seed of 42. Min–Max
scaling parameters are fitted exclusively on the training data and then applied unchanged
to the validation and test sets. After the Dirichlet allocation, SMOTE and majority-class
under-sampling are performed independently within each client’s local training data; no
resampling is applied to the validation or test sets [49].
The federated non-IID setting is constructed using label-distribution skew. The train-
ing data are distributed among 10 simulated clients using a Dirichlet distribution with
concentration parameter αDir = 0.5. Smaller values of αDir produce more heterogeneous
class distributions across clients. The validation and test sets are not Dirichlet-partitioned
and remain fixed across all experiments to ensure a consistent evaluation of the global
model. The resulting dataset sizes and train–validation–test partitions are summarized
in Table 3. The client-level class proportions resulting from the Dirichlet-based non-IID
allocation are reported in Table 4, illustrating the heterogeneous label distribution across
the 10 federated clients.
Table 3. Dataset partitioning used in the experiments.
Dataset
Total
Train (80%)
Validation (10%)
Test (10%)
CICIDS2017
2,830,743
2,264,594
283,074
283,075
Edge-IIoTset
2,219,201
1,775,361
221,920
221,920
Table 4. Class distribution across the 10 federated clients under Dirichlet label skew (αDir = 0.5).
Client
Benign (%)
Attack (%)
1
78.4
21.6
2
34.7
65.3
3
62.1
37.9
4
18.9
81.1
5
71.5
28.5
6
43.8
56.2
7
84.2
15.8
8
29.6
70.4
9
55.3
44.7
10
39.4
60.6
https://doi.org/10.3390/electronics15204584
```

### PDF page 17

[View original page](assets/page-017.png)

```text
Electronics 2026, 15, 4584
17 of 27
Table 3 reports the dataset-level sample counts before local resampling, while Table 4
reports the client-level benign and attack distributions prior to local balancing. Since
SMOTE and undersampling are applied independently within each client’s training subset
after non-IID partitioning, the validation and test sets remain unchanged and are not
involved in any resampling operation.
4.2. Implementation Details
FLZT-IDS is implemented in Python 3.11.9 using PyTorch 2.4.1, PyTorch Geometric
2.6.1, and Flower 1.11.1 [50]. Model training uses the Adam optimizer with a learning
rate of 0.01, weight decay of 1 × 10−5, β1 = 0.9, β2 = 0.999, and ϵ = 10−8. Model pa-
rameters are initialized using Xavier uniform initialization for the learnable linear and
graph-convolutional layers, while recurrent weights in the BiLSTM use orthogonal initial-
ization. Bias terms are initialized to zero. A fixed random seed of 42 is used for Python,
NumPy, and PyTorch to improve reproducibility.
Experiments are executed on an Apple MacBook Pro with an M3 chip, 8-core CPU,
10-core GPU, and 16 GB RAM running macOS Sonoma 14.x. PyTorch’s Metal Performance
Shaders (MPS) backend is used for hardware acceleration during model training, with CPU
execution used for operations not supported by MPS. The model is trained for 100 global
communication rounds across 10 simulated clients under non-IID settings, with five local
epochs per round and a batch size of 128. The complete simulation parameters and system
configuration are summarized in Table 5.
Table 5. Simulation parameters and system configuration for FLZT-IDS.
Parameter
Value
Operating System
macOS Sonoma 14.x
Frameworks
PyTorch, PyTorch Geometric, Flower
Learning Rate
0.01
Batch Size
128
Epochs per Round
5
Number of Clients
10
Update Clipping Norm (C)
1.0
Client Sampling Rate (q)
0.2 (2 of 10 clients/round)
Privacy Failure Probability (δ)
10−5
Privacy Accountant
RDP Accountant
Default Privacy Noise Scale (σ)
0.8
Communication Threshold (ϵcomm)
0.01
Trust Threshold (τthreshold)
0.6
Trust Weights (α, β, γ)
(0.4, 0.3, 0.3)
Trust Evidence Window (W)
5 communication rounds
Initial Trust Score (τ0
i )
0.7
Global Rounds
100
4.3. Performance Metrics
To evaluate the effectiveness of FLZT-IDS, we employ a combination of traditional
classification metrics and system-level evaluation criteria. These metrics are designed to
capture not only the detection capability of the model but also its robustness against
adversarial behaviors, privacy tradeoffs, and communication efficiency in federated
IoT environments.
For this binary classification setting, the Attack class is treated as the positive class
and the Benign class as the negative class; therefore, Precision, Recall, and F1-score are
reported for the positive Attack class rather than as macro-, micro-, or weighted-average
multiclass measures.
https://doi.org/10.3390/electronics15204584
```

### PDF page 18

[View original page](assets/page-018.png)

```text
Electronics 2026, 15, 4584
18 of 27
•
Accuracy: Measures the overall correctness of the model by computing the ratio
of correctly classified samples (both benign and malicious) to the total number of
samples. This provides a high-level view of model performance but can be misleading
in imbalanced datasets.
•
Precision: Indicates the proportion of true positive attack detections among all samples
predicted as attacks. A high precision score reflects a low false alarm rate and is
particularly important for minimizing unnecessary responses to benign activities.
•
Recall: Measures the proportion of actual attacks correctly identified by the model. A
high recall ensures that the system can effectively detect intrusions and minimize the
likelihood of undetected threats.
•
F1-Score: Serves as the harmonic mean of precision and recall, offering a balanced
metric that is especially useful in the presence of class imbalance. It provides a single
score that reflects both false positives and false negatives.
•
False Positive Rate (FPR): Quantifies the proportion of benign samples incorrectly
classified as attacks. A low FPR is essential to maintain trust in the IDS and avoid alert
fatigue in practical deployments.
•
Communication Overhead: Represents the average volume (in kilobytes) of model
updates transmitted per client in each communication round. This metric evaluates the
scalability and communication efficiency of FLZT-IDS, which is critical for resource-
constrained IoT networks.
Beyond these traditional evaluation metrics, we conduct targeted experimental anal-
yses to validate specific components of the proposed architecture, including its privacy-
preserving and adversarial-resilient capabilities:
•
Privacy–Utility Tradeoff: We measure the detection accuracy of FLZT-IDS as the LDP
noise scale (σ) varies. This quantifies the impact of added noise on model performance
and validates the effectiveness of our SALDP scheme.
•
Adversarial Robustness: To evaluate the resilience of FLZT-IDS against malicious
clients, we simulate model poisoning scenarios where a subset of clients submit
manipulated updates. The model’s accuracy degradation under increasing attack rates
is observed and compared with baseline models lacking Zero-Trust validation.
•
Trust Filtering Impact: We assess how varying the trust threshold τthreshold affects the
inclusion or exclusion of clients during the FL process. This experiment demonstrates
the effectiveness of the Zero-Trust module in filtering unreliable participants and its
impact on detection quality and false positives.
•
Communication Efficiency: We evaluate the communication overhead by measuring
the volume of model updates transmitted during federated training. This analysis
quantifies the communication savings achieved by the adaptive update and trust-
filtering mechanisms.
These metrics collectively ensure a comprehensive and rigorous evaluation of FLZT-
IDS across multiple performance dimensions, aligning with the key contributions of this
work: privacy preservation, scalability, adversarial robustness, and accuracy.
4.4. Baseline Comparisons
FLZT-IDS is compared against three recent and representative FL-based IDS frame-
works that reflect different design priorities:
FL-IDS [40]: A classical FL-based IDS using the FedAvg algorithm and a shallow
artificial neural network (ANN). While it supports collaborative learning across distributed
nodes, it lacks built-in privacy mechanisms or adversarial filtering strategies.
https://doi.org/10.3390/electronics15204584
```

### PDF page 19

[View original page](assets/page-019.png)

```text
Electronics 2026, 15, 4584
19 of 27
FedGAT [41]: An attention-based graph neural network model operating in a feder-
ated setting. It effectively models relational dependencies in network flows but does not
apply differential privacy or incorporate trust-aware participation.
Fed-ANIDS [51]: An anomaly-based IDS that leverages autoencoders in a federated
setting. It is designed to preserve user data privacy by avoiding raw data sharing but does
not utilize graph structures or Zero-Trust validation.
All models are trained and evaluated under identical experimental settings on CI-
CIDS2017 and Edge-IIoTset datasets. FLZT-IDS consistently demonstrates superior de-
tection capability, efficient communication, and robust defense against adversarial and
untrusted participants, as shown in the following results.
5. Results & Analysis
5.1. Ablation Study on Model Components
To assess the contribution of each key component within the FLZT-IDS framework,
we perform an ablation study by selectively disabling individual modules, including GNN,
Attention-based BiLSTM, SALDP, and the Zero-Trust mechanism. The performance is
evaluated on both CICIDS2017 and Edge-IIoTset datasets using standard metrics. The
results are summarized in Table 6.
Table 6. Performance of FLZT-IDS under different ablation scenarios on CICIDS2017 and Edge-
IIoTset datasets.
Model Variant
CICIDS2017
Edge-IIoTset
Accuracy
Precision
Recall
F1
FPR
Comm. (KB)
Accuracy
Precision
Recall
F1
FPR
Comm. (KB)
FLZT-IDS (Full)
97.8%
98.1%
97.5%
97.8%
1.9%
34.2
96.2%
96.9%
95.4%
96.1%
2.3%
33.5
w/o GNN
94.2%
95.3%
92.4%
93.8%
3.5%
33.1
92.6%
93.5%
90.1%
91.8%
4.1%
32.8
w/o BiLSTM
93.6%
94.8%
91.1%
92.9%
3.9%
33.6
91.8%
93.0%
89.2%
91.0%
4.5%
33.2
w/o SALDP
96.5%
97.0%
95.1%
96.0%
2.4%
31.8
94.7%
95.5%
93.2%
94.3%
2.8%
31.4
w/o Zero-Trust
95.1%
95.8%
94.3%
95.0%
3.1%
36.9
93.5%
94.1%
92.2%
93.1%
3.6%
35.7
We observe that the full FLZT-IDS model achieves the highest overall performance,
with 97.8% accuracy and 97.8% F1-score on CICIDS2017, and 96.2% accuracy and 96.1%
F1-score on Edge-IIoTset. When the GNN component is removed, both datasets show a
substantial drop in recall and F1-score, indicating that relational pattern recognition is
critical for detecting coordinated and structural attacks.
Eliminating the BiLSTM module results in further reductions in recall, especially for
time-dependent attacks. This highlights the importance of modeling sequential dependen-
cies in network traffic.
Disabling SALDP reduces both detection accuracy and precision on the two datasets,
while slightly lowering communication overhead due to the removal of privacy-preserving
operations. This indicates that, under the evaluated configuration, SALDP provides pri-
vacy protection without degrading the overall detection performance of the complete
FLZT-IDS framework.
Finally, removing the Zero-Trust component leads to a noticeable rise in FPR and com-
munication overhead, suggesting that trust-aware filtering contributes to in securing the ag-
gregation process and reducing noisy contributions from potentially compromised clients.
The ablation results show that removing individual components changes one or more
measured outcomes, indicating that the components contribute differently to detection,
privacy, and communication performance.
5.2. Model Accuracy Comparison over Rounds
Figure 4 presents the accuracy progression of FLZT-IDS and three baseline models, FL-
IDS, FedGAT, and Fed-ANIDS, evaluated over 100 global communication rounds on both
https://doi.org/10.3390/electronics15204584
```

### PDF page 20

[View original page](assets/page-020.png)

```text
Electronics 2026, 15, 4584
20 of 27
CICIDS2017 and Edge-IIoTset datasets. Across both datasets, FLZT-IDS demonstrates faster
convergence and consistently higher accuracy compared to other models. On CICIDS2017,
FLZT-IDS reaches an accuracy of 97.8%, outperforming Fed-ANIDS (94.5%), FedGAT
(91.5%), and FL-IDS (89.6%). A similar trend is observed on Edge-IIoTset, where FLZT-
IDS achieves 96.2% accuracy, ahead of Fed-ANIDS (89.0%), FedGAT (86.3%), and FL-
IDS (85.2%).
The superior performance of FLZT-IDS is attributed to the integration of GNN for
structural threat detection, Attention-based BiLSTM for temporal anomaly modeling,
and its Zero-Trust framework for filtering untrusted participants. Moreover, the privacy-
preserving aggregation techniques do not significantly hinder learning progression, demon-
strating the model’s efficiency under secure federated settings. These results validate
the robustness and adaptability of FLZT-IDS in diverse IoT environments and empha-
size its effectiveness in delivering high detection accuracy while preserving privacy and
model integrity.
Figure 4. Accuracy progression over communication rounds for FLZT-IDS and baseline models on
the CICIDS2017 and Edge-IIoTset datasets.
5.3. Privacy–Utility and Privacy Attack Analysis
Figure 5 evaluates the privacy–utility behavior of FLZT-IDS under different Gaus-
sian noise multipliers. In addition to detection accuracy, the cumulative privacy loss is
computed using the RDP accountant with clipping norm C = 1.0, client sampling rate
q = 0.2, privacy failure probability δ = 10−5, and 100 communication rounds. As expected,
increasing the noise multiplier provides a stronger privacy guarantee at the expense of
some detection utility.
Figure 5. Accuracy comparison of FLZT-IDS and baseline models under varying differential privacy
noise scales (σ) on CICIDS2017 and Edge-IIoTset datasets.
https://doi.org/10.3390/electronics15204584
```

### PDF page 21

[View original page](assets/page-021.png)

```text
Electronics 2026, 15, 4584
21 of 27
Table 7 reports the cumulative privacy budgets obtained after 100 communication
rounds. The results demonstrate the expected inverse relationship between the Gaussian
noise multiplier and the accumulated privacy loss: larger values of σ produce smaller ε
values and therefore stronger differential privacy.
Table 7. Differential privacy accounting after 100 communication rounds (C = 1.0, q = 0.2, and
δ = 10−5).
Noise Multiplier (σ)
δ
Final ε
0.8
10−5
25.6
1.0
10−5
18.2
1.2
10−5
12.9
1.5
10−5
9.3
2.0
10−5
6.2
To complement the analytical privacy accounting, we additionally evaluate resistance
to membership inference attacks (MIA). The attacker attempts to determine whether a given
sample was included in the training data based on the output confidence of the trained
global model. Attack accuracy and the area under the receiver operating characteristic
curve (AUC) are reported, where values approaching 50% attack accuracy and an AUC
of 0.5 indicate performance close to random guessing. The non-private model is used as
the reference setting and is compared with SALDP under progressively stronger Gaussian
noise levels.
As shown in Table 8, the non-private model is more susceptible to membership
inference, with an attack accuracy of 69.4% and an AUC of 0.741. Applying SALDP progres-
sively reduces the attacker’s ability to distinguish training members from non-members.
At σ = 0.8, the attack accuracy decreases to 58.7%, while increasing the noise multiplier
to σ = 2.0 reduces it to 51.6%, with an AUC of 0.519, approaching random guessing. This
increased privacy is accompanied by the expected utility trade-off, with model accuracy
decreasing from 97.8% without DP to 88.7% at σ = 2.0. These results complement the
analytical (ε, δ) accounting by demonstrating reduced empirical information leakage under
progressively stronger privacy settings.
Table 8. Membership inference attack evaluation under different privacy settings on CICIDS2017.
Setting
Attack Accuracy
Attack AUC
Model Accuracy
Without DP
69.4%
0.741
97.8%
SALDP (σ = 0.8)
58.7%
0.608
94.6%
SALDP (σ = 1.2)
54.1%
0.555
92.3%
SALDP (σ = 2.0)
51.6%
0.519
88.7%
5.4. Adversarial Robustness Against Malicious Clients
To evaluate the robustness of FLZT-IDS under adversarial conditions, we simulate an
untargeted sign-flipping model-poisoning attack. Malicious clients reverse the direction
of their locally computed model updates before transmission, i.e., ∆wadv
i
= −∆wi. The
attackers have access only to their own local data and model updates and do not know the
private data of other clients or the server-side trust scores. We evaluate malicious-client
ratios of 0%, 10%, 20%, and 30%, corresponding to zero, one, two, and three malicious
clients, respectively, in the 10-client simulation. Figure 6 presents the resulting accuracy
trends on CICIDS2017 and Edge-IIoTset.
FLZT-IDS consistently demonstrates superior resilience. On CICIDS2017, while FL-IDS
and FedGAT drop to 72.3% and 76.5% respectively at 30% poisoning, FLZT-IDS maintains
https://doi.org/10.3390/electronics15204584
```

### PDF page 22

[View original page](assets/page-022.png)

```text
Electronics 2026, 15, 4584
22 of 27
an accuracy of 89.3%. Similarly, on Edge-IIoTset, FLZT-IDS retains 87.1% accuracy, signifi-
cantly higher than Fed-ANIDS (75.0%) and FedGAT (70.3%). This robustness stems from
the Zero-Trust-based participant verification mechanism and gradient-deviation screening,
which filter potentially corrupted updates before the accepted updates are combined us-
ing secure weighted FedAvg. These results demonstrate robustness under the evaluated
untargeted poisoning scenario within the 10-client simulation. Because the experiments
involve at most three malicious clients, the findings should not be interpreted as a general
robustness guarantee against larger-scale, adaptive, or stealthy federated attacks.
Figure 6.
Accuracy degradation of FLZT-IDS and baseline models under varying malicious
client ratios.
5.5. Impact of Trust Filtering
To assess the effectiveness of the Zero-Trust mechanism in FLZT-IDS, we examine
how varying the trust threshold τthreshold affects detection performance. Figure 7 presents
accuracy and FPR for different τ values ranging from 0.4 to 0.7 on both CICIDS2017 and
Edge-IIoTset datasets.
As shown in subplots (a) and (c), accuracy improves with increasing τ, peaking
at τ = 0.6 for both datasets. Beyond this point, accuracy slightly declines, suggesting
that excessively strict filtering may exclude benign clients. Specifically, on CICIDS2017
(Figure 7a), accuracy rises from 93.4% at τ = 0.4 to 97.8% at τ = 0.6, then drops slightly
to 96.5% at τ = 0.7. On Edge-IIoTset (Figure 7c), a similar trend is observed with peak
accuracy at 96.2%.
Correspondingly, subplots (b) and (d) show that FPR decreases as τ increases, demon-
strating improved attack detection reliability.
For instance, the FPR on CICIDS2017
decreases from 5.8% to 2.7% as τ increases from 0.4 to 0.6, before rising slightly at 0.7
(Figure 7b). The Edge-IIoTset dataset exhibits similar behavior, with the lowest FPR of
3.1% at τ = 0.6 (Figure 7d). At the selected threshold τ = 0.6, the false rejection rate,
defined as the proportion of benign participating clients incorrectly excluded by the trust
filter, was 4.6% on CICIDS2017 and 5.1% on Edge-IIoTset, indicating that the selected
threshold provides a reasonable balance between malicious-client filtering and benign-
client participation. These results confirm that the Zero-Trust-based filtering mechanism in
FLZT-IDS effectively improves detection accuracy and reduces false alarms, provided the
trust threshold is optimally tuned.
https://doi.org/10.3390/electronics15204584
```

### PDF page 23

[View original page](assets/page-023.png)

```text
Electronics 2026, 15, 4584
23 of 27
Figure 7. (a–d) Effect of varying the trust threshold τthreshold on accuracy and false positive rate (FPR)
in FLZT-IDS.
5.6. Communication Efficiency
Figure 8 compares the cumulative communication overhead incurred by FLZT-IDS
against three baseline models, across varying numbers of global rounds (25, 50, 75, and
100). The results on both CICIDS2017 and Edge-IIoTset datasets demonstrate that FLZT-IDS
achieves significant reductions in communication cost over time.
This improvement is attributed to two key factors: (i) the integration of an adaptive
update mechanism, which limits model transmissions to only significant updates based
on the threshold ϵcomm, and (ii) the trust filtering process that excludes low-trust clients,
further minimizing unnecessary communication. Compared to FL-IDS, FLZT-IDS reduces
cumulative communication overhead by more than 30% after 100 rounds on both datasets,
while still achieving superior detection accuracy.
Figure 8. Cumulative communication overhead (in KB) of FLZT-IDS and baseline models across
different numbers of global communication rounds on CICIDS2017 and Edge-IIoTset datasets.
https://doi.org/10.3390/electronics15204584
```

### PDF page 24

[View original page](assets/page-024.png)

```text
Electronics 2026, 15, 4584
24 of 27
6. Discussion
6.1. Strengths & Improvements over Existing Work
The proposed FLZT-IDS framework introduces a comprehensive enhancement over
existing federated IDS by simultaneously addressing privacy, trust, efficiency, and adapt-
ability challenges in IoT environments. Unlike conventional FL-based IDS models that
rely solely on federated updates, FLZT-IDS integrates a Zero-Trust mechanism to filter out
potentially malicious or unreliable clients based on dynamic trust scores. This results in
higher model robustness under adversarial conditions, as demonstrated in our poisoning
resilience experiments.
From a privacy standpoint, FLZT-IDS incorporates SALDP with bounded update
clipping and Gaussian perturbation. Privacy loss is quantified using (ε, δ)-DP and RDP
accounting over the complete federated training process, while membership inference
experiments provide an empirical assessment of information leakage. The privacy–utility
analysis demonstrates the trade-off between stronger privacy protection and intrusion-
detection performance.
In terms of detection capability, the hybrid deep learning architecture combining GNN
and Attention-based BiLSTM allows the model to capture both structural and sequential
attack patterns more effectively. This dual-view learning strategy contributes to consistently
higher accuracy and lower FPR on both CICIDS2017 and Edge-IIoTset datasets.
Furthermore, FLZT-IDS demonstrates substantial reductions in communication over-
head due to its adaptive update strategy. By limiting unnecessary transmissions, the
framework improves communication efficiency in bandwidth-constrained federated IoT
environments. However, the present study does not provide a complete computational-cost
evaluation in terms of FLOPs, memory usage, inference latency, energy consumption, or
cryptographic processing time; these aspects require evaluation on representative resource-
constrained edge devices in future work.
6.2. Limitations & Future Directions
Despite its strengths, FLZT-IDS has several limitations that open avenues for future
research. First, the current implementation assumes a simulated federated environment
with a fixed number of IoT clients. While this setup supports controlled and reproducible
evaluation, it may not fully capture the variability of real-world federated networks,
where client participation, connectivity, computational capacity, and data distributions can
change dynamically.
Second, although the trust-score mechanism filters potentially malicious clients, it
relies on predefined indicators such as recent activity, protocol compliance, and anomaly
confidence. More sophisticated trust inference mechanisms, including reinforcement learn-
ing or reputation-based approaches, could further improve resilience against stealthy or
evolving adversaries.
Third, the current adversarial evaluation is limited to the spec-
ified poisoning scenario and a 10-client simulation. Therefore, the reported robustness
results should not be interpreted as a general guarantee against broader classes of at-
tacks. Future work should evaluate adaptive and stealthy attacks and include comparisons
with dedicated robust aggregation methods such as Trimmed Mean, Krum, RFA, FLTrust,
and FoolsGold.
Fourth, although the proposed model combines GNN and BiLSTM components to
improve relational and temporal intrusion detection, the associated computational require-
ments may remain non-trivial for resource-constrained edge devices. Lightweight model
variants, model compression, or hardware-aware neural architecture search could therefore
be explored to improve deployment feasibility.
https://doi.org/10.3390/electronics15204584
```

### PDF page 25

[View original page](assets/page-025.png)

```text
Electronics 2026, 15, 4584
25 of 27
In addition, the current implementation operationalizes Zero-Trust principles through
continuous server-side score-based client verification and filtering. It does not constitute a
complete identity-management or cryptographic Zero-Trust authentication architecture.
Future extensions could incorporate stronger identity verification and authentication mech-
anisms to provide a more comprehensive Zero-Trust implementation.
Finally, extending FLZT-IDS to support asynchronous federated learning and per-
sonalized client models could further improve adaptability in heterogeneous environ-
ments, particularly where client availability, data distributions, and device capabilities
vary significantly.
7. Conclusions
This paper introduced FLZT-IDS, a Zero-Trust-enabled federated learning framework
for secure and privacy-preserving intrusion detection in IoT environments. By integrating
GNN and Attention-based BiLSTM, the framework captures both relational and sequen-
tial attack patterns. The incorporation of SALDP provides a quantifiable privacy–utility
trade-off, supported by cumulative (ε, δ) privacy accounting and membership inference
evaluation. Furthermore, the Zero-Trust mechanism filters unreliable clients and improves
resilience under the evaluated model-poisoning scenario.
Experiments on CICIDS2017 and Edge-IIoTset show that FLZT-IDS achieves 97.8% and
96.2% accuracy, respectively, while reducing transmitted model-update volume relative to
FL-IDS through adaptive communication and trust-based client filtering. Under the evalu-
ated 10-client simulation, the framework also maintains higher detection performance than
the selected baselines under the tested poisoning conditions. These findings demonstrate
the potential of FLZT-IDS within the controlled experimental setting while recognizing
that larger-scale, real-world federated deployments may introduce additional variability
in client participation, communication, computational capacity, and adversarial behavior.
Future work will therefore focus on broader client populations, real-world edge-device
evaluation, stronger adversarial settings, and a more complete assessment of cryptographic
and computational overhead.
Author Contributions: Conceptualization, S.K.B.; Methodology, S.K.B. and M.A.; Validation, C.W.
and M.A.; Investigation, M.A.; Writing—original draft, S.K.B.; Writing—review & editing, M.A. and
C.W.; Supervision, C.W. and S.K.B.; Project administration, C.W. and S.K.B.; Funding acquisition,
C.W. and S.K.B., All authors have read and agreed to the published version of the manuscript.
Funding: This work is supported by National Natural Science Foundation of China Project, Project
No.: 52577124, and 52207125, and the Key Research and Development Program of Hunan Province
Project, Project No.: 2024JK2040 and also Shaoyang University Doctoral Research Start-up Special
Project, Project No.: 25KYQD166.
Data Availability Statement: The raw data supporting the conclusions of this article will be made
available by the authors on request.
Conflicts of Interest: The authors declare no conflict of interest.
References
1.
Abasi, A.K.; Aloqaily, M.; Ouni, B.; Guizani, M.; Debbah, M.; Karray, F. A survey on securing 6G wireless communications based
optimization techniques. In Proceedings of the 2023 International Wireless Communications and Mobile Computing (IWCMC); IEEE:
New York, NY, USA, 2023; pp. 216–223.
2.
Rahmani, A.M.; Bayramov, S.; Kiani Kalejahi, B. Internet of things applications: Opportunities and threats. Wirel. Pers. Commun.
2022, 122, 451–476. [CrossRef] [PubMed]
3.
Al-Haija, Q.A.; Droos, A. A comprehensive survey on deep learning-based intrusion detection systems in Internet of Things (IoT).
Expert Syst. 2025, 42, e13726. [CrossRef]
https://doi.org/10.3390/electronics15204584
```

### PDF page 26

[View original page](assets/page-026.png)

```text
Electronics 2026, 15, 4584
26 of 27
4.
Bikila, D.D.; ˇCapek, J. Machine Learning-Based Attack Detection for the Internet of Things. Future Gener. Comput. Syst. 2025,
166, 107630. [CrossRef]
5.
Lin, Y.D.; Chan, W.H.; Lai, Y.C.; Yu, C.M.; Wu, Y.S.; Lee, W.B. Enhancing can security with ML-based IDS: Strategies and efficacies
against adversarial attacks. Comput. Secur. 2025, 151, 104322. [CrossRef]
6.
Friha, O.; Ferrag, M.A.; Shu, L.; Maglaras, L.; Choo, K.K.R.; Nafaa, M. FELIDS: Federated learning-based intrusion detection
system for agricultural Internet of Things. J. Parallel Distrib. Comput. 2022, 165, 17–31. [CrossRef]
7.
Yang, H.; Hu, K.; Wang, H.; Hong, W.; Wang, X.; Wang, H.; Song, Y.; Liu, Z. BCLIP-ADer: A Bayesian prompt contrastive
language-image pretraining method for catenary component anomaly detection in electrified railways. IEEE Trans. Transp. Electrif.
2026, 12, 7522–7534.
8.
Yan, J.; Chen, B.; Zhang, F.; Cheng, Y.; Wang, H.; Wang, H.; Wang, M.; Li, T.; Zhang, W. Meta-Learning-Based Graph Convolutional
Wavelet Network for Intelligent Dynamic Modeling of High-Speed Rail Subsystems. IEEE Trans. Veh. Technol. 2026, early access.
[CrossRef]
9.
Nahar, N.; Andersson, K.; Schelén, O.; Saguna, S. A Survey on Zero Trust Architecture: Applications and Challenges of 6G
Networks. IEEE Access 2024, 12, 94753–94764. [CrossRef]
10.
Agrawal, S.; Sarkar, S.; Aouedi, O.; Yenduri, G.; Piamrat, K.; Alazab, M.; Bhattacharya, S.; Maddikunta, P.K.R.; Gadekallu, T.R.
Federated learning for intrusion detection system: Concepts, challenges and future directions. Comput. Commun. 2022, 195,
346–361. [CrossRef]
11.
Fedorchenko, E.; Novikova, E.; Shulepov, A. Comparative review of the intrusion detection systems based on federated learning:
Advantages and open challenges. Algorithms 2022, 15, 247. [CrossRef]
12.
Asad, M.; Moustafa, A.; Yu, C. A critical evaluation of privacy and security threats in federated learning. Sensors 2020, 20, 7182.
[CrossRef] [PubMed]
13.
Mishra, S.; Kshirsagar, V.; Dwivedula, R.; Hota, C. Attention-based bi-lstm for anomaly detection on time-series data. In
Proceedings of the International Conference on Artificial Neural Networks; Springer: Berlin/Heidelberg, Germany, 2021; pp. 129–140.
[CrossRef] [PubMed]
14.
Saputra, I.P.; Utami, E.; Muhammad, A.H. Comparison of anomaly based and signature based methods in detection of scanning
vulnerability. In Proceedings of the 2022 9th International Conference on Electrical Engineering, Computer Science and Informatics (EECSI);
IEEE: New York, NY, USA, 2022; pp. 221–225.
15.
AlYousef, M.Y.; Abdelmajeed, N.T. Dynamically detecting security threats and updating a signature-based intrusion detection
system’s database. Procedia Comput. Sci. 2019, 159, 1507–1516. [CrossRef]
16.
Mutambik, I. An Efficient Flow-Based Anomaly Detection System for Enhanced Security in IoT Networks. Sensors 2024, 24, 7408.
[CrossRef] [PubMed]
17.
Ghazi, D.S.; Hamid, H.S.; Zaiter, M.J.; Behadili, A.S.G. Snort Versus Suricata in Intrusion Detection. Iraqi J. Inf. Commun. Technol.
2024, 7, 73–88. [CrossRef]
18.
Kumar, V.; Sinha, D. A robust intelligent zero-day cyber-attack detection technique. Complex Intell. Syst. 2021, 7, 2211–2234.
[CrossRef] [PubMed]
19.
Ullah, I.; Mahmoud, Q.H. Design and development of a deep learning-based model for anomaly detection in IoT networks. IEEE
Access 2021, 9, 103906–103926. [CrossRef]
20.
Asad, M.; Otoum, S.; Shaukat, S. Clients eligibility-based lightweight protocol in federated learning: An ids use-case. IEEE Trans.
Netw. Serv. Manag. 2024, 21, 3759–3774. [CrossRef]
21.
Chauhan, P.; Atulkar, M. An efficient centralized DDoS attack detection approach for Software Defined Internet of Things. J.
Supercomput. 2023, 79, 10386–10422. [CrossRef]
22.
Bhavsar, M.; Bekele, Y.; Roy, K.; Kelly, J.; Limbrick, D. FL-IDS: Federated learning-based intrusion detection system using edge
devices for transportation IoT. IEEE Access 2024, 12, 52215–52226. [CrossRef]
23.
Alsaleh, S.; Menai, M.E.B.; Al-Ahmadi, S. Federated Learning–Based Model to Lightweight IDSs for heterogeneous IoT Networks:
State-of-the-Art, Challenges and Future Directions. IEEE Access 2024, 12, 134256–134272. [CrossRef]
24.
Asad, M.; Moustafa, A.; Ito, T. Fedopt: Towards communication efficiency and privacy preservation in federated learning. Appl.
Sci. 2020, 10, 2864. [CrossRef]
25.
Chinamanagonda, S. Zero Trust Security Models in Cloud Infrastructure-Adoption of zero-trust principles for enhanced security.
Acad. Nexus J. 2022, 1, 1–19.
26.
Al Ridhawi, I.; Aloqaily, M. Zero-Trust UAV-enabled and DT-supported 6G Networks. In Proceedings of the GLOBECOM
2023—2023 IEEE Global Communications Conference; IEEE: New York, NY, USA, 2023; pp. 6171–6176.
27.
Ridhawi, I.A.; Otoum, S.; Aloqaily, M. Decentralized zero-trust framework for digital twin-based 6G. arXiv 2023, arXiv:2302.03107.
28.
Ismail, M.; Abd El-Gawad, A.F. Revisiting zero-trust security for internet of things. Sustain. Mach. Intell. J. 2023, 3, 1–8. [CrossRef]
29.
Nowroozi, E.; Haider, I.; Taheri, R.; Conti, M. Federated learning under attack: Exposing vulnerabilities through data poisoning
attacks in computer networks. IEEE Trans. Netw. Serv. Manag. 2025, 22, 822–831. [CrossRef]
https://doi.org/10.3390/electronics15204584
```

### PDF page 27

[View original page](assets/page-027.png)

```text
Electronics 2026, 15, 4584
27 of 27
30.
Blika, A.; Palmos, S.; Doukas, G.; Lamprou, V.; Pelekis, S.; Kontoulis, M.; Ntanos, C.; Askounis, D. Federated Learning For
Enhanced Cybersecurity And Trustworthiness In 5G and 6G Networks: A Comprehensive Survey. IEEE Open J. Commun. Soc.
2024, 6, 3094–3130. [CrossRef]
31.
Khacha, A.; Saadouni, R.; Harbi, Y.; Aliouat, Z.; Gherbi, C.; Harous, S. Privacy-Preserving in Agricultural IoT: Intrusion Detection
Using Federated Learning and CNN. In Proceedings of the 2024 International Conference on Advanced Aspects of Software Engineering
(ICAASE); IEEE: New York, NY, USA, 2024; pp. 1–7.
32.
Bonawitz, K.; Eichner, H.; Grieskamp, W.; Huba, D.; Ingerman, A.; Ivanov, V.; Kiddon, C.; Koneˇcn`y, J.; Mazzocchi, S.; McMahan,
B.; et al. Towards federated learning at scale: System design. Proc. Mach. Learn. Syst. 2019, 1, 374–388.
33.
Moustafa, A.; Asad, M.; Shaukat, S.; Norta, A. Ppcsa: Partial participation-based compressed and secure aggregation in federated
learning. In Proceedings of the International Conference on Advanced Information Networking and Applications, Toronto, ON,
Canada, 12–14 May 2021; pp. 345–357.
34.
McMahan, B.; Moore, E.; Ramage, D.; Hampson, S.; Y Arcas, B.A. Communication-efficient learning of deep networks from
decentralized data. In Proceedings of the Artificial Intelligence and Statistics; PMLR: New York, NY, USA, 2017; pp. 1273–1282.
35.
Znidi, F.; Morsy, M.; Rathore, H. Future on Wheels: Safeguarding Privacy in Tomorrow’s Connected Vehicles-FUTURE-SP. IEEE
Access 2024, 12, 179857–179878. [CrossRef]
36.
Sobchuk, V.; Pykhnivskyi, R.; Barabash, O.; Korotin, S.; Omarov, S. Sequential intrusion detection system for zero-trust cyber
defense of IOT/IIOT networks. Adv. Inf. Syst. 2024, 8, 92–99. [CrossRef]
37.
Asad, M.; Alhasawi, Y. SIAD: A low-latency AI-driven software architecture for anomaly detection in industrial IoT environments.
Clust. Comput. 2026, 29, 427. [CrossRef]
38.
Cai, M.; Zhang, Z.; Wu, G.; Chai, T. XMatchAD: A Cross-Modal Matching Perspective on Reconstruction-based Anomaly
Detection. IEEE Trans. Image Process. 2026, 35, 8443–8455. [CrossRef] [PubMed]
39.
Soomro, P.D.; Fu, X.; Banbhrani, S.K.; Ali, A.; Asad, M. Federated learning based deep learning framework for robust object
detection in indoor and outdoor environments. Comput. Electr. Eng. 2026, 133, 110910. [CrossRef]
40.
Lazzarini, R.; Tianfield, H.; Charissis, V. Federated learning for IoT intrusion detection. AI 2023, 4, 509–530. [CrossRef]
41.
Wu, J.; Qiu, G.; Wu, C.; Jiang, W.; Jin, J. Federated learning for network attack detection using attention-based graph neural
networks. Sci. Rep. 2024, 14, 19088. [CrossRef] [PubMed]
42.
He, Y.; Huang, D.; Chen, L.; Ni, Y.; Ma, X. A survey on zero trust architecture: Challenges and future trends. Wirel. Commun. Mob.
Comput. 2022, 2022, 6476274. [CrossRef]
43.
Zhang, K.; Sun, J.; Feng, Q.; Huang, X.; Jiang, C.; Hossain, M.S. Joint optimization of fairness and energy efficiency in zero-trust
federated learning for consumer internet of things: A lossy communication perspective. IEEE Trans. Consum. Electron. 2024, 71,
1156–1166. [CrossRef]
44.
Li, Z.; He, Y.; Yu, H.; Kang, J.; Li, X.; Xu, Z.; Niyato, D. Data heterogeneity-robust federated learning via group client selection in
industrial IoT. IEEE Internet Things J. 2022, 9, 17844–17857. [CrossRef]
45.
Zhang, H.; Cao, T. A Hybrid Approach to Network Intrusion Detection Based On Graph Neural Networks and Transformer
Architectures. In Proceedings of the 2024 14th International Conference on Information Science and Technology (ICIST); IEEE: New York,
NY, USA, 2024; pp. 574–582.
46.
Sivamohan, S.; Sridhar, S.; Krishnaveni, S. An effective recurrent neural network (RNN) based intrusion detection via bi-
directional long short-term memory. In Proceedings of the 2021 International Conference on Intelligent Technologies (CONIT); IEEE:
New York, NY, USA, 2021; pp. 1–5.
47.
Panigrahi, R.; Borah, S. A detailed analysis of CICIDS2017 dataset for designing Intrusion Detection Systems. Int. J. Eng. Technol.
2018, 7, 479–482.
48.
Ferrag, M.A.; Friha, O.; Hamouda, D.; Maglaras, L.; Janicke, H. Edge-IIoTset: A New Comprehensive Realistic Cyber Security
Dataset of IoT and IIoT Applications for Centralized and Federated Learning. IEEE Access 2022, 10, 40281–40306. [CrossRef]
49.
Shelke, M.S.; Deshmukh, P.R.; Shandilya, V.K. A review on imbalanced data handling using undersampling and oversampling
technique. Int. J. Recent Trends Eng. Res. 2017, 3, 444–449. [CrossRef]
50.
Beutel, D.J.; Topal, T.; Mathur, A.; Qiu, X.; Fernandez-Marques, J.; Gao, Y.; Sani, L.; Li, K.H.; Parcollet, T.; de Gusmão, P.P.B.; et al.
Flower: A friendly federated learning research framework. arXiv 2020, arXiv:2007.14390.
51.
Idrissi, M.J.; Alami, H.; El Mahdaouy, A.; El Mekki, A.; Oualil, S.; Yartaoui, Z.; Berrada, I. Fed-anids: Federated learning for
anomaly-based network intrusion detection systems. Expert Syst. Appl. 2023, 234, 121000. [CrossRef]
Disclaimer/Publisher’s Note: The statements, opinions and data contained in all publications are solely those of the individual
author(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to
people or property resulting from any ideas, methods, instructions or products referred to in the content.
https://doi.org/10.3390/electronics15204584
```
