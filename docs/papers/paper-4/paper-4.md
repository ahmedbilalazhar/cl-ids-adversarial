# A Federated and Incremental Network Intrusion Detection System for IoT Emerging Threats

**Authors:** Raffaele Carillo; Francesco Cerasuolo; Giampaolo Bovenzi; Domenico Ciuonzo; Antonio Pescapé

**Publication:** IEEE Transactions on Network and Service Management (2026).

**Publication DOI:** https://doi.org/10.1109/TNSM.2026.3675031

**Verified free PDF:** https://domenicociuonzo.wordpress.com/wp-content/uploads/2026/03/early_access_tnsm26_fedcil_ids.pdf

**Downloaded version:** Public author early-access manuscript. The template header says XXXX 2025; the registered journal publication is 2026. Cite the journal DOI/year, not the template header.

**Qualification:** Q1, COMPUTER SCIENCE, INFORMATION SYSTEMS. Journal rankings use the 2024 JIF category quartile (June 2025 JCR), not an asserted 2026 ranking.

**Integrity:** 17 pages; 1,656,380 bytes; SHA-256 `e3ff129bed5e9a00fca8cd4b8705fa3a7903cbaa4adb9d542fd6ed563fc274a4`. Verified 8 October 2026.

## Reading and extraction note

The PDF is the authoritative complete manuscript. Below is automatic page-level text extraction, not a newly authored summary or a verbatim-quality transcription. Two-column order, formulas, ligatures and table spacing can be imperfect. Every page has a rendered PNG in `assets/` for inspecting figures, equations and tables at their original locations. Publication metadata is saved alongside the images. The technical review is in [the selection audit](../phase2-selection-audit.md).

## Full manuscript text


### PDF page 1

[View original page, figures and tables](assets/page-001.png)

```text
IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. XX, NO. X, XXXX 2025                                                                                                               1
      A Federated and Incremental Network Intrusion
            Detection System for IoT Emerging Threats

                                      Raffaele Carillo, Francesco Cerasuolo, Giampaolo Bovenzi,
                    Domenico Ciuonzo,Senior Member, IEEE, Antonio Pescapé,Senior Member, IEEE





   Abstract—Ensuring network security is increasingly challeng-                  NIDS by broadening threat coverage, it raises seriousprivacy
ing,  especially  in  the  Internet  of  Things  (IoT)  domain,  where           concerns, making itimpractical in most real-world scenarios
threats are diverse, rapidly evolving, and often device-specific.                involving user data. Notably, recent studies have investigated
Hence, Network Intrusion Detection Systems (NIDSs) require (i)                   either  CIL  or  FL  for  NIDS,  but  largely  in  isolation:  CIL
being trained on network traffic gathered in different collection                approaches typically assume centralized access to all traffic
points to cover the attack traffic heterogeneity, (ii) continuously
learning emerging threats (viz.,0-day attacks), and (iii) be able                data, while FL ones usually consider a fixed and pre-defined
to take attack countermeasures as soon as possible.                              set of attack classes. Only a limited number of works explore
In  this  work,  we  aim  to  improve  Artificial  Intelligence  (AI)-           their integration, and those that do often focus on simplified
based  NIDS  design  &  maintenance  by  integrating  Federated                  scenarios such as binary detection tasks, overlapping classes,
Learning (FL) and Class Incremental Learning (CIL). Specifi-                     or post-hoc analysis. Consequently, the problem of incremen-
cally, we devise a Federated Class Incremental Learning (FCIL)
framework–suited  for  early-detection  settings—that  supports                  tally learningnew, client-specific attack classesfromdecen-
decentralized  and  continual  model  updates,  investigating  the               tralized, non-IID datain anearly-detectionsetting remains
non-trivial  intersection  of  FL  algorithms  with  state-of-the-art            largely unaddressed.
CIL techniques to enable scalable, privacy-preserving training                      In  this  work,  we  propose  a  FCIL  framework  for  NIDS
in highly non-IID environments. We evaluate FCIL on three IoT
datasets across different client scenarios to assess its ability to              that simultaneously addresses the challenges of incremental
learn new threats and retain prior knowledge. The experiments                    learning and decentralized training. By integrating CIL, the
assess potential key challenges in generalization and few-sample                 system can continuously incorporate new attack classes with-
training,  and  compare  NIDS  performance  to  monolithic  and                  out  forgetting  previously  learned  threats,  while  FL  enables
centralized baselines.                                                           collaborative model training across distributed clients, ensur-
   Index Terms—Network Intrusion Detection Systems, Internet                     ing scalability and preserving data privacy. This combination
of Things, Federated Learning, Class Incremental Learning, 0-                    allows our NIDS to adapt in real time to emerging threats in
day attacks                                                                      heterogeneous network environments [6–8].

                          I.  INTRODUCTION                                          Combining FL and CIL for designing NIDS posesunique
                                                                                 and still largely unaddressed challenges. First, the non-IID na-
      YBER-ATTACKS have increased rapidly in the last few                        ture of client data means new attack classes may emerge only
C     years, reaching an impressive number of600million of                       on specific clients, leading to imbalanced updates and poor
attacks performed daily [1], highlighting the urgent need for                    generalization. Second, catastrophic forgetting is intensified,
service providers to adopt a more proactive role in ensuring                     as clients may observe only new classes, causing the global
the  integrity,  confidentiality,  and  availability  of  data  across           model to overwrite knowledge of previously learned attacks.
digital infrastructures. In this scenario, NIDSs are central to                  Third,  the  stability–plasticity  dilemma  becomes  even  more
securing  modern  networks,  shifting  from  static,  signature-                 pronounced, as each client must not only retain previously
based methods to adaptive approaches powered by Machine                          learned  classes  while  learning  new  (local)  ones,  but  also
Learning (ML) and Deep Learning (DL) techniques [2]. This                        integrate new disjoint attack classes from other clients.
need  is  even  more  pronounced  in  the  IoT  domain,  where                      Hence, thecontributionsof this work are the following:
resource-constrained and heterogeneous devices increase the
attack surface. For instance, IoT nodes are often hijacked into                     •we  formalize  and  study  a  realistic  FCIL  problem  for
botnets for large-scale DDoS attacks (e.g., Mirai) [3], or run                         NIDS,whereearlydetection,client-specificnovelattacks,
outdated firmware that enables persistent exploitation [4].                            andnon-IID decentralized datajointly coexist, a setting
   However,  AI-based  NIDS  cannot  easily  adapt  to  emerg-                         that has not been systematically addressed in prior work;
ing (0-day) attacks, as updating them requirestraining-from-                        •we provide a comprehensive analysis of how state-of-
scratch, which is both storage- and computation-intensive [5].                         the-art (SOTA) CIL strategies behave in federated envi-
Moreover,  while  cross-network  data  sharing  could  enhance                         ronments, revealing non-trivial interactions with different
                                                                                       aggregation  schemes  (FedAvg,FedProx,  andFedDyn)
     R.  Carillo,  F.  Cerasuolo,  G.  Bovenzi,  D.  Ciuonzo,  and  A.  Pescapé        and limitations, absent in centralized setups;
are   with   the   Department   of   Electrical   Engineering   and   Information   •we  investigate  realistic  federated  configurations  with
Technologies   (DIETI)   at   the   University   of   Naples   Federico   II,   Italy  varying numbers of clients (i.e.,2and5), each intro-
(name.surname@unina.it). The illustrations in this manuscript include images
downloaded fromflaticon.comandfontawesome.com.                                         ducing asingle, disjoint novel attack, thereby explicitly
```


### PDF page 2

[View original page, figures and tables](assets/page-002.png)

```text
IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. XX, NO. X, XXXX 2025                                                                                                               2

                                   Table I: Studies proposing CIL and/or FL techniques for NIDS from2022onwards in chronological order.

















































































     Paper          Early                                              CIL                                                     FL                               Few  IoT
                     NIDS   DL     NIDSTask      Setup            Approach            Increments   Setup       Approach       #Clients   DC           Shot         Threats      TO     Input Data        ML/DLModel

   [9] (2022)      ✗    ✗     mMD✓        HardSamplingMCA ✗              -                 -         -      ✗    #         B        Statistics         AB, HT
                                                               GDUMB,iCaRL,
                                                               GSS,ER,ASER,
   [10] (2023)         ✗       ✓      mMD          ✓          MIR,AGEM,SSR,              MCA          ✗              -               -        -         ✗             #           F        Statistics       1D-CNN
                                                              NCM,SLDA,EWC,
                            stressing FCIL-designed NIDS under severe class imbal-LwF                                             directions of our research.
   [11] (2023)      ✓   ✓    mMD✓             I                               2RNN                  SCAance and client heterogeneity;                                                    DIR, WIN,PL, IAT,   LSTM
                                                                                         MCA      ✗              -                 -         -      ✗    #         S                      TTL, FLG
                        •we evaluate FCIL-designed NIDS inreal-world scenar-FT,iCaRL,BFS-NID
   [12] (2023)         ✓    ios, assessing its ability to (i) generalize across networks✓mMD✓FOSTER,IDFSCIL,LIMIT,C-FSCILMCA✗-       -        -        ✓            II.  RELATEDWORKS#B      PB*          Transformer

   [13] (2024)      ✓   ✗     mMD✓       FT,EEILand  (ii)  learn  effectively  from  a  limited  number  of,LwF*           MCA ✗              -                 -         -      ✗    #         BDIR, WIN,PL, IAT,MLP
                            samples.                                                                                                  In this section, we review the use of CIL and FL in theTTL, FLG
                                                               FT,EWC,LwF,                                                        context of NIDS. First, we discuss approaches that apply CIL
   [14] (2024)         ✗       ✓      mMD          ✓        iCaRL,SimpleCIL,SPCIL        MCA          ✗              -               -        -         ✗             #           B       Statistics*      ResNet18
                       The rest of the paper is organized as follows. The studiesFT,FT-Mem,LwF,                                   to NIDS in Sec.II-A, followed by an overview of FL-based
   [15] (2025)      ✓   ✓                     bMDdealing with CIL and FL for NIDS are reviewed in Sec.AC      ✓iCaRL+,BiC,EWCSCA  ✗              -                 -         -      ✓             B                     PL, IAT,II.methods in Sec.II-B. Then, we examine recent efforts thatDIR, WIN,       2D-CNN
                   Then, Sec.IIIdescribes the FCIL procedure. The experimentalEEIL,LUCIR                                          integrate both paradigms—CIL and FL—for NIDS (Sec.II-C).
   [16] (2025)         ✓       ✓       bMD         ✓          FT,FT-Mem,BiC              MCA          ✗              -               -        -         ✗                         B        PL, IAT,         2D-CNN
                   setup and results are reported in Sec.mMD                  IVandV, respectively.                               Finally, Sec.II-Dpositions our work within this landscape. ADIR, WIN,
   [17] (2022)     Lastly, Sec.✗✗ VIconcludes our work, highlighting also futurebMDAD✗-    -          ✓          FedAvg†          summary of the reviewed literature is provided in Tab.II.8✗✗G#SStatistics   MLPAE

   [18] (2022)      ✗   ✓    mMD✗                  -                        -       ✓        FedAvg          2     ✗     ✗    #         B        Statistics           GRU
                                                                                                                                     5                                                                        DNN
   [19] (2022)         ✗       ✓      mMD          ✗                  -                    -          ✓           FedAvg            10        ✗         ✗             G#          B        Statistics         CNN
                                                                                                                                    15                                                                        RNN
                                                                                                                                     2
   [20] (2023)      ✗   ✓    mMD✗                  -                        -       ✓         DAFL                                   5        ✗     ✗    #         B        Statistics           CNN
                                                                                                                                     7
   [21] (2023)         ✗       ✗        AD         ✗                  -                    -          ✓           FedAvg            10        ✗         ✗             #           B        Statistics         AAE
                                                                                                                 FedProx
   [22] (2024)      ✗   ✓    mMD✗                  -                        -       ✓        FedAvg                                         24      ✗     ✗    #         B        Statistics           CNN

   [23] (2022)      ✓   ✓    bMD ✓          SOINN-RBF         MCA ✓                                              FedAvg,            10   ✗     ✗    #         B                 IAT, IDL,
                                                                                                               Fed-SOINNCMFL,                                                             ACT, BR        2D-CNN

   [24] (2023)         ✗       ✗       bMD         ✓                 FT                  MCA          ✓           FedAvg            10        ✗         ✗             #           F        Statistics         MLP
   [25] (2023)      ✗   ✓    mMD✓             iCaRL         MCA ✓        FedAvg†       3     ✗     ✗              F        Statistics           CNN
                                                                                                                                                                                           PS, PL,
   [26] (2024)         ✓       ✓      mMD          ✓              iCaRL+                 MCA          ✓           GLFC              10        ✗         ✗             #           B      WIN, FLG,IAT, DIR, 2D-CNN

                                                                                                                                                                                          ACT, IDL
   [27] (2024)      ✗   ✓    mMD✓                                FT-Mem,iCaRL,WA,DER                    MCA ✓        FedAvg†       3     ✗     ✗              F        Statistics1D-CNN

                                                                                                               EvoFedIDS,
                                                                                                                FedSpace,FedSI                                                            IAT, DIR,PS, PL,
   [28] (2024)         ✓       ✓       bMD         ✓              iCaRL+                 SCA          ✓           GLFC               5        ✗         ✗             #           B      WIN, FLG,          2D-CNN
                                                                                                                 FedProtoFCIL,                                                            ACT, IDL

   [29] (2024)      ✗   ✓    mMD✓               EWC                MCA ✓        FedAvg†       50   ✗     ✗    G#         S        Statistics        CNN-GRU
                                                                                                                 FedAvg,
                                                                  GEM,EWC                                      SCAFFOLD,FedProx,
   [30] (2025)         ✗       ✓      mMD          ✓               iCaRL                 MCA          ✓          FedMD,             10        ✗         ✗             #           F        Statistics        BERT
                                                                                                                 FedGKTFedDF,


                                       bMD                     iCaRL+,BiC,                                        FedAvg             2                                                     PL, IAT,
This work(2025)   ✓   ✓               mMDAC        ✓          BiC+,MEMENTOMEMENTO+               SCA  ✓,         FedProxFedDyn       5      ✓    ✓             B                         DIR, WIN,TTL, FLG  2D-CNN

Deep Learning (DL);Task: binary Misuse Detection (bMD), multi-class Misuse Detection (mMD), Anomaly Detection (AD), Attack Classification (AC);CIL Increments: Single Class Addition (SCA),
Multi-ClassAddition(MCA);DisjointClasses(DC);TrafficObject(TO):Biflow(B),Session(S),Flow(F);InputData:PacketLength(PL),Inter-ArrivalTime(IAT),Direction(DIR),TCPWindowsSize
(WIN), TCP Flags (FLG), Time-To-Live (TTL), Payload Bytes (PB), Idle Time (IDL), Active Time (ACT), Byte Rate (BR), L4 Payload Size (PS), Contextual Features (CF);Machine Learning (ML)/DL
Model: Convolutional Neural Network (CNN), Long Short Term Memory (LSTM), Multi Layer Perceptron (MLP), Gated Recurrent Unit (GRU), Auto Encoder (AE), Hoeffding Tree (HF), AdaBoost (AB);
*: image-like format;†: with modifications;✓present,✗lacking; : more than one IoT dataset;G#: a single IoT dataset;#: no IoT dataset.
```


### PDF page 3

[View original page, figures and tables](assets/page-003.png)

```text
IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. XX, NO. X, XXXX 2025                                                                                                               3


A. Incremental Learning for NIDS                                                  thenetwork dimensionsinto (i)cross-deviceand (ii)cross-
   In this section, we review the literature on CIL applied to                    silosettings.  The  former  involves  many  personal  devices
NIDS, focusing on approaches that adapt existing intrusion                        with unstable connections and variable data, while the latter
detectors to counter emerging attack types and anomalies. In                      features fewer entities—e.g., organizations—with more stable,
the  literature,  CIL  approaches  are  divided  intothree  main                  high-bandwidth links and less frequent communication [33].
familiesbased  on  model  expansions  [31]:(i) fine-tuning,                       Furthermore, client data can be characterized as eitherinde-
expanding  the  model  head  and  updating  the  entire  model                    pendently and identically distributed(IID) ornon-IID. In the
with  the  incremental  training  set;(ii) fixed-representation,                  former setting, data across clients is statistically consistent and
expanding  the  model  head  and  freezing  parts  of  the  pre–                  independent. Conversely, in the latter case, data samples are
trained model (viz., backbone and/or old head), definitively                      interdependent and drawn from different distributions, often
training the non-frozen parts;(iii)model-growth, adding new                       reflecting the inherent heterogeneity among clients [33].
models or  layers  to accommodate  new knowledge.  All the                           Among the reviewed literature, all works deal withhorizon-
reviewed works are from the fine-tuning family, except for                        talFL, sharing feature space while having a disjoint sample
I2RNN[11]  andSPCIL[14],  which  employ  model-growth                             space.Moreover,alltheworksimplementacross-devicesetup,
solutions.  Notably,  the  fixed-representation  family  remains                  with local training performed on edge devices, and deal with
largely unexplored for network intrusion detection tasks, as                      classes and samples shared among clients, resulting in data
freezing the base model may undermine the plasticity required                     distributions that are only partially non-IID (column “DC”).
to learn new patterns (see column “CIL Approach” in Tab.I                            As for FL algorithm (column “FL approach”), the majority
for further details).                                                             of  works  leverageFedAvg[17–19, 21, 22].  Additionally,
   As for incremental episodes (column “CIL Increments”),                         other works propose minor modifications toFedAvg, such as
most of the reviewed works adopt multi-class increments—                          incorporating weighted averaging schemes and client selection
i.e., adding more new classes per episode—while only [11,15]                      based on contribution significance [20], while others adopt
explore the single-class addition scenario, which more closely                    more  sophisticated  FL  algorithms,  such  as  FedProx  [21].
mirrors  real-world  deployment  with  new  attacks  typically                    Interestingly, Rey et al. [17] investigate techniques todefend
appearing individually over time.                                                 against adversarial clients aiming to poison the global model.
   Reviewed work deals with the Multi-class Misuse Detection                         Finally, all the revised studies address the mMD task em-
(mMD) task—i.e., distinguishing among benign and all the                          ploying (supervised) DL models [18–20,22], except for [17]
attack classes—, while Binary Misuse Detection (bMD)—i.e.,                        and [21] leveraging the (unsupervised) AutoEncoders (AEs) to
differentiatingbenignandmalicioustraffic—isalsoconsidered                         perform the Anomaly Detection (AD) task—that is, training
in [16]. In addition, Cerasuolo et al. [15] decompose the intru-                  only on the benign class and recognizing attacks as anomalies
sion detection process into two sequential tasks: a bMD task                      or out-of-distribution samples.
and an Attack Classification (AC) task—i.e., categorization of                    C. Federated Incremental Learning for NIDS
malicious traffic into different attack types.                                       In  this  section,  we  review  existing  work  that  integrates
   Crucially,  most  of  these  studies  focus  onpost-mortem                     incremental expansion of NIDS (i.e., CIL) with decentralized
detection—that is, they do not performearly detection(see                         training  approaches  (i.e.,  FL),  namely,  FCIL.  Notably,  all
column  “Early  Detection”)—typically  relying  on  statistics                    these studies focus on a multi-class addition (column “CIL
computed over the entire traffic object (see column “Input                        Setup”)—only [28] addresses single-class addition—and con-
Data”).  In  contrast,  a  subset  of  works  avoid  (handcrafted)                sider non-disjoint classes among clients (column “DC”).
feature summarization, using raw fields from packet headers                          Among   these   studies,   most   adopt   CIL   approaches
or payloads as direct inputs to the model. These approaches                       which  are  baselines  in  network-related  tasks,  except  for
typically leverage only the firstN      p packets of a flow to build              SOINN-RBF[23]— leveraging self-organizing incremental neu-
NIDS that supportearly-stage decisionsand enabletimely,                           ral networks (SOINN) in conjunction with Radial Basis Func-
proactive responseto threats.                                                     tion (RBF), incrementally mapping the original input into a

B. Federated Learning for NIDS                                                    higher-dimensional space.
                                                                                     Regardingthe FLstrategy,most employFedAvgeither inits
   In  this  section,  we  review  the  literature  on  FL  applied               originalformorwithminoradaptations,asseenin[25,27,29].
to  NIDS.  FL  allows  NIDS  to  be  trained  on  decentralized                   Notably, Jin et al. [25] leverage class prototypes and impor-
attack  data,  preserving  privacy  and  minimizing  malicious                    tance factors for client models in the aggregation process. On
traffic transmission. This is especially valuable for sensitive or                the other hand, Mao et al. [27] and Quyen et al. [29] weight
large-scale data, enabling collaborative and privacy-preserving                   each client model duringFedAvgaggregation according to
training [8]. In the literature,two main FL familiesare com-                      the  size  of  its  training  dataset.  In  addition,  several  studies
monly distinguished based on how data is distributed among                        adopt alternative FL aggregation algorithms as performance
clients:  (i)horizontal  (or  homogeneous)  FL,  where  clients                   baselines for comparison, including FedSI [28], CMFL [23],
share the same feature space but each possesses a different                       FedSpace  [28],  GLFC  [26, 28],  FCIL  [28],  FedProto  [28],
set of data samples; and (ii)vertical (or heterogeneous) FL,                      FedProx [30], SCAFFOLD [30], FedMD [30], FedDF [30],
in which clients hold different features corresponding to the                     and FedGKT [30], or define new approaches, such as EvoFe-
same sample set [32]. Additionally, FL can be classified by                       dIDS [28] or Fed-SOINN [23].
```


### PDF page 4

[View original page, figures and tables](assets/page-004.png)

```text
IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. XX, NO. X, XXXX 2025                                                                                                               4


   As for the detection task, the majority focus on supervised                                              III.  METHODOLOGY
misuse detection—either bMD [23,24,28] or mMD [25,26,                                 We  begin  by  presenting  the  core  methodologies  behind
29]. Notably, Jin et al. [25] detect both known and zero-day                      CIL (Sec.III-A) and FL (Sec.III-B). Then, we introduce the
intrusions and continuously adapt to emerging threats, but also                   NIDS-focused unified framework for FCIL (Sec.III-C), which
perform mMD to discriminate among known classes.                                  integrates the key principles of both paradigms.

D. Literature Gap & Positioning
   In this work, we deal withincrementalanddecentralized                          A. Class Incremental Learning
NIDS  to  tackle  the  evolving  nature  of  cyber-attacks  and                       In  this  work,  we  adopt  the  CIL  paradigm  within  DL
associated privacy concerns. Differently from previous works                      architectures.  To  provide  context,  we  first  introduce  the
considering only CIL [9–16] or FL [18–22] separately, which                       notation   about   data   and   fundamental   concepts   underly-
eitherassumecentralizeddataavailabilityorafixedandclosed                          ing  both  approaches.  Notably,  the  training  dataset  (D=
set of attack classes, we explore how NIDScan continuously                        {(x   1,y1),...,(x    N,yN)}) is composed ofNinput samples,
learn in a decentralized fashion.                                                 whereeachsample(e.g.,abiflow)x    n∈Xislabeledasbenign
   Equally important, in contrast with existing literature on                     traffic or attack class (i.e.,y       n∈K= 1,2,3,...).
FCIL for NIDS [23–25,27–29], which mostly assumes full-                               Considering a generic DL architecture, it is composed of
traffic or post-mortem analysis and overlooks the constraints                     two  parts:  abackbone,  in  charge  of  the  feature  extraction
of timely intrusion response, we consider anearly-detection                       ϕ:X → Vobtaining from the input (x) its latent space
setup and investigate the mMD task, along with its decoupled                      representationv(viz., feature vector); ahead, transforming
counterpart bMD, followed by the AC task. Separating bMD                          feature vectors into logitsh(ϕ(x)) =o(x)∈O. Then, logits
and AC decouples detection from classification performance.                       are converted into class probabilities via the usual softmax
Unlike mMD, this distinction reveals whether a system can                         activation function, defined as
only  detect  threats  and  correctly  identify  them  separately,
enabling a clearer assessment of its capabilities.                                                                                         |K|X
   Furthermore,inordertosupportlow-resourceenvironments,                                    [softmax(x)]                  k =p   k(x;K) =e            ok(x)   /eoj(x)   ,      (1)
we adopt neither model-growth approaches (e.g.DER)—given                                                                                   j=1
their increasing storage and communication costs, which are                       and predictions are obtained asˆy≜argmax           k∈K {p  k(x;K)}.
particularly detrimental in federated settings—, nor baseline                         The incremental NIDS aims to train a set of parameters
approachesfornetwork-relatedtasks(i.e.,FT,EWC,iCaRL,and                           θto learn a functionγ:X → K, withγ(x) =  ˆy∈ K
WA), which have been shown to be non-effective for network                        representing the predicted label for inputx(i.e., legitimate
traffic data [34]. Conversely,we focus on cutting-edge CIL                        traffic or a specific attack type).
approaches  from  fine-tuning  family,  such  asiCaRL+[35],                           The CIL problem can be formulated as follows: at each
BiC[36] andBiC                   + [37],MEMENTO[38] andMEMENTO                                     + [37],episode, a set of new classesK           new is introduced, along with
in theirdecentralized flavor. This choice is motivated by the                     a  labeled  datasetD           new.  The  goal  is  to  update  an  existing
lightweight nature of fine-tuning approaches, which impose                        NIDS—previously trained onD      old—to integrate knowledge
minimal storage and communication overhead when compared                          fromK        new while preserving its ability to recognize the pre-
to model-growth solutions.                                                        viously learned classesK           old, thereby enabling discrimination
   To  account  for  non-IID  and  unbalanced  attack  distribu-                  over the complete class set (K all =K   old∪Knew). Some CIL
tions,  we  move  beyond  thede  factostandardFedAvgand                           methods additionally exploit a subset of samples from the old
includeFedProxandFedDyn, which explicitly handle client                           classes, retained in memory, to reinforce prior knowledge dur-
heterogeneity and update stability, enablinga more realistic                      ing incremental updates. In such cases, training is performed
evaluation of CIL–FL integration.                                                 on the combined datasetD           mem∪Dnew [39].
   Further, most prior FCIL studies assume overlapping attack                         In the following, the CIL approaches employed in this work
classes or the simultaneous introduction of multiple classes,                     are presented. Specifically, we consider approaches fromfine-
which mitigates class imbalance and simplifies aggregation.                       tuningfamily,  as  they  offer  the  highest  scalability  without
In contrast, we consider amore general scenarioin which                           increasing the resource demand. [31]. Notably, all these ap-
each client introduces asingle, distinct novel attack, resulting                  proaches  are  considered  as  a  baseline  for  the  incremental
in  client-specific  attack  distributions—i.e.,  no  class  overlap              process—i.e.,FT-Mem—or  have  proven  to  be  effective  for
betweenclients.Moreover,weconsidertheadditionofasingle                            network traffic classification [34,35,38] or adaptive NIDS
attack (class) per client—a more challenging scenario than                        task [15]. They utilize an exemplar memory and often employ
those considered in prior work, due to the pronounced im-                         a composite loss function to guide the training process, with
balance between new and existing classes [34]. Additionally,                      an optional bias correction layer to preventtask-recency bias.
adding a single attack per client reflects realistic scenarios
where new attacks emerge sparsely and unevenly across the                         FT-Mem—Fine-Tuning  with  Memory[34]: built on top of
network. Lastly, we assess scalability by varying the number                      Fine-Tuning  (FT)  approach  [40],  it  stores  a  small  part  of
of clients in federated networks, evaluating how the resulting                    old classes samples—selected with herding strategy—and use
FCIL NIDS handles real-world challenges like cross-network                        them in the incremental training (viz.,D=D               new∪Dmem) to
generalization and limited data availability.                                     reduce catastrophic forgetting, by refreshing old knowledge.
```


### PDF page 5

[View original page, figures and tables](assets/page-005.png)

```text
IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. XX, NO. X, XXXX 2025                                                                                                               5


iCaRL+—Incremental Classifier and Representation                                      In  this  work,  we  consider  across-siloFL  setting,  i.e.,
Learning  Plus[35]:  it  adaptsiCaRLto  network  traffic,                         a  federated  network  with  a  small  number  of  clients  rep-
incorporating both rehearsal strategy (through herding selec-                     resenting  different  organizations  or  geographical  collection
tion)  and  a  composite  loss  function  with  equally  weighted                 points.  Each  client  corresponds  to  a  group  of  IoT  devices
classificationandKnowledgeDistillation(KD)terms(λ class=                          (e.g., gateways, edge nodes, or administrative domains) rather
λdist=1). Differently fromiCaRLemploying a Nearest Mean                           than individual constrained sensors, and clients collaboratively
Classifier,iCaRL+leverage a model head that dynamically                           train a global NIDS; while each client observes traffic from
expands and activates through the softmax function.                               different attack classes (non-IID), all employ the same feature
BiC—Bias   Correction[36]:  it  introduces  anadditional                          space (horizontalFL). Communication is therefore limited to
layer—parametrized withαandβ—to correct new classes                               exchanging model updates, whose size—on the order of a few
logits to reduce the task recency and sample biases towards                       MB per round for our architecture—is compatible with NB-
new classes. The incremental training is led by a composite                       IoT, LTE-M, and typical edge/cloud backhaul links assumed
loss function with classification and KD terms (weighted by                       in cross-silo IoT and industrial deployments [41]. Supporting
λclass =|K   new|/|K   all|andλ       dist = 1−λ     class, respectively).        fully constrained end devices would instead require additional
BiCretains  a  balanced  small  set  of  biflows—also  called                     mechanisms such as model compression or hierarchical FL.
correction set—composed of⌈P%·N                   old⌉for each old and                In the experiments, we leverage different FL approaches to
new class, whereN          old represents the number of old samples               aggregate models from different federated clients. In detail,
foreachK       old.1 Therefore,theadditionallayeristrainedonthis                  we  employ  three  approaches,  described  in  the  following.
dataset (viz., correction set) to determine the two parameters                    Notably, we exclude some approaches from our analysis as
with both backbone and head frozen.                                               they compute and share local prototypes across the federa-
MEMENTO—distill augMented knowlEdge, sMooth nEw iN-                               tion,introducingsignificantcomputationalandcommunication
formation,  and  recTify  bOth[38]:  built  uponBiC,  it  is                      overhead—e.g., FedProK [42], LGA [43].
defined depending on the scenario considered. Notably, for                        Federated  Averaging  (FedAvg)[44]: each client performs
few-class  increments,MEMENTOintroduces  a  series  of  en-                       local  model  update  by  minimizing  its  own  loss  function
hancements for improving network traffic classification per-                      Fm(θ), yielding updated parametersθ                        rm = argminθFm(θ).
formance. These include (i) biflow augmentation techniques                        These locally-updated models are then transmitted to a central
using static traffic primitives applied to the IAT—viz., jittering                server, which computes the global model by averaging the
       IATjit≜iat1  ···  iat Np+ρ1  ···  ρ Np,                                collected client parameters.

                                                                                                                            MX
whereρ          i∼N(µ,σ),i= 1,...,N             P, and translating                                             θr =  1           θrm                               (2)
         IATtra =iat1  ···  iat Np+ρ ···  ρ ,                                                                      M   m=1

whereρ∼N(µ,σ)—, (ii) the construction of a balanced vali-                         FedProx[45]: built uponFedAvg, it is based on the assump-
dationsetfromexemplarsmemorytoleadincrementaltraining                             tion that clients may have very different data distributions and
across tasks, and (iii) the use of a higher temperature in the                    may  not  converge  when  usingFedAvg.  For  these  reasons,
classification loss to encourage softer probability distributions                 FedProxadds  aproximal  termto  the  local  (viz.  client)
andreduceoverconfidence.Lastbutnotleast,MEMENTOapplies                            objective function to keep local updates closer to the global
(iv) output smoothing during knowledge distillation to better                     model. At each communication roundr, clientmcomputes
handle biflows belonging to newly-introduced classes.                             updated parameters asθ   rm = argminθLm(θ)by minimizing
                                                                                  the following augmented objective function:
B. Federated Learning                                                                             Lm(θ) =F       m(θ)+    µ    

θ−θ     r−1 

2,              (3)
   In a typical FL setup, a network ofMclientsc                   1,c2,...,cM                                               2
collaboratively trains a shared model. During each commu-                         whereF          m(·)is the standard local loss on clientm, andµ
nication  roundr, mth  client  first  updates  its  local  model                  controls the strength of the regularization term. The squared
θrm  using  its  private  datasetD           m,  tailoring  the  training  to     ℓ2-norm keeps each client’s model close to the previous global
its task. Once local training is complete, clients send their                     parametersθ                  r−1    , enhancing robustness to data heterogeneity.
updated model parameters to a central federated server, which                     Server aggregation is then performed analogously asFedAvg.
coordinates  the  training  process.  The  server  aggregates  the                FedDyn[46]: it aims to improve the communication efficiency
received  models  to  produce  an  updated  global  model  that                   ofFedAvgby dynamically modifying the client objective with
captures the collective knowledge of all clients. This global                     a penalty term so that when model parameters converge, they
model is then redistributed to the clients, who resume local                      do  so  in  stationary  points  of  the  global  empirical  loss.  In
training  based  on  the  aggregated  update.  This  process  is                  particular, the linear and quadratic penalty terms minima are
iteratively repeated forRcommunication rounds.                                    consistent with the global loss stationary point. The penalty


    1The number of per-class biflows in the correction set is limited by the      term is based on the local and server models, namely:
old classes, which are fewer in memory than the new-class biflows of the                                                                  

θ−θ     r−1 

2,(4)
current episode.                                                                    Lm(θ) =F       m(θ)−⟨∇F          m(θ r−1m  ),θ⟩+      α2
```


### PDF page 6

[View original page, figures and tables](assets/page-006.png)

```text
IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. XX, NO. X, XXXX 2025                                                                                                               6



















Figure 1: Visual representation of the overall proposal. Each client incrementally trains its local NIDS, including new attacks,
and simultaneously participates in the federated network’s collaborative information exchange. This process converges to a
global NIDS, then distributed across all clients, to perform (binaryandmulticlass) misuse detection and attack classification.


where the first term represents the standard local empirical                      form of non-independent and identically distributed (non-IID)
loss (e.g., cross-entropy); the second term (⟨∇F      m(θ r−1m  ),θ⟩)             data distribution among the clients, who must also mitigate
subtracts a linear approximation based on past gradients to                       catastrophic forgetting as they learn new classes.
compensate for bias in the client distribution; and the third

θ−θ     r−1 

2,encouragesthelocalmodeltostaycloseOn the top of that, integrating CIL into a federated setting
term, α2                                                                          introduces  specific  design  challenges.  While  simplerfine-
to the previous global modelθ          r−1    , similar toFedProx. Server         tuningmethods can be directly federated, those including post-
aggregation is performed similarly toFedAvgandFedProx.                            trainingtechniqueslikebiascorrection[36,38]requiretailored
                                                                                  solutions.Inthiswork,weleveragetwodifferentsolutions[37]
C. Federated Class Incremental Learning                                           which capitalize FL framework.
   In the FCIL setup, each client incrementally introduces a                          In the first one, all clients share the same bias layer for new
new  set  of  classes,  with  the  objective  of  training  a  global             classes  ¯Knew, similar toBiC-based solutions in a centralized
NIDScapableofaccuratelyclassifyingbothpreviouslylearned                           setting.  Each  client  updates  this  layer  using  its  own  data
and newly introduced classes across all clients. The overall                      (D mem∪Dnewm   ), the server averages the clients’ parameters
procedure is depicted in Fig.1.                                                   (α newm  ,βm)to compute the global correction, and sent the
   Formally, at the generic (incremental) episode,mth client                      averaged correction to all clients for the next round:
                                                                                                                      oold(x)
in the federated network adds a set of new classesK           newm   . The             ¯o(x) =        PM         αnew                                        (5)
FCIL procedure begins with a base model—trained on previ-                                           1              m  onew(x)+β       m·1|¯Knew|
                                                                                                   M      m=1
ously seen classesK           old during an earlier federated (possibly           In the second approach, each client maintains a personalized
incremental) iteration—which is then distributed to all clients                   bias layer for its new classes. At each round, clientc         m updates
joining the network. Accordingly, all the clients start the incre-                only its local parameters(α                    new
mental process from the same model, effectively representing                      the server. The server stacks all client-specific corrections tom  ,βm)and shares them with
a scenario where clients can join the network asynchronously                      support classification across all new classes:
and require a synchronization step. In a federated setting,m                                                                                   
client performs local training for a fixed number of epochs                                                               oold(x)
before synchronizing with the server and other clients across                                               αnew1   onew1    +β   1·1|Knew                (6)
                                                                                                                                          1   |
Rcommunication rounds.                                                                            ¯o(x) =                      ...
   In  the  FCIL  context,  the  goal  is  to  update  an  existing                                            αnew
NIDS—previously trained onD      old—to integrate knowledge                                                      M  onewM   +β   M·1|KnewM  |
from ¯Knew≜S{Knewm  }Mm=1    (i.e. the set of new classes from                    The set of all correction parameters(α                    newm  ,βm)Mm=1    are sent
allthe involved clients) while preserving its ability to recog-                   back to all clients for next round. We denote the averaged
nizethepreviouslylearnedclassesK           old.Hence,discrimination               variant byA, and the client-specific one byA            +.
capabilities of the updated NIDS are required to be over the                          We  note  that  the  proposed  FCIL  framework  does  not
complete class setK    all =K   old∪ ¯Knew.                                       incur  additional  asymptotic  computational  overhead  com-
   Despite the generality of the above FCIL formulation (and                      pared to standard FL. The overall complexity is dominated
of  the  proposed  solutions),  in  this  work  we  are  concerned                by  local  training  at  each  client  and  can  be  expressed  as
with the case whereeach client introduces a distinct set of                       O( PMm=1   RENmP), whereMis the number of clients,R
                                                                      ′.  This
new  classes,  i.e.K                 newm   ∩ Knewm′    =∅,  form̸=m              the number of communication rounds,Ethe number of local
setting poses a significant challenge, as it leads to an extreme                  training epochs,N            m the number of training samples at client
```


### PDF page 7

[View original page, figures and tables](assets/page-007.png)

```text
IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. XX, NO. X, XXXX 2025                                                                                                               7

















                    (a)TON_IoT                                                                                               (c)Edge-IIoTset
                                                                          (b)IoT-NID











Figure 2: Biflows distributions for the IoT datasets employed. Green bars represent the benign class across all three datasets.
Sankey diagrams show specific attacks per category, with colored circles indicating the datasets that contain each attack.


m(i.e., the size ofD       mem∪Dnewm   ), andPthe number of train-                involved [16]. For instance, in the DoS category, most datasets
able model parameters. The server-side aggregation of client                      (exceptTON_IoT) include UDP floods, while HTTP and SYN
parametershaslinearcomplexitywithrespecttothenumberof                             floods are common across all.TON_IoTuniquely has a generic
clientsandparameters,i.e.O(MP)percommunicationround.                              TCP flood; ACK and ICMP floods are specific toIoT-NIDand
We emphasize that the additional components introduced by                         Edge-IIoTset, respectively. Info gathering attacks mostly in-
the FCIL framework—such as shared or client-specific bias                         volvevariousscans:port(Edge-IIoTset,IoT-NID,TON_IoT),
layers  for  incremental  class  correction—do  not  affect  the                  OS (IoT-NID,Edge-IIoTset), vulnerability (Edge-IIoTset),
asymptotic complexity. Their cost is negligible compared to                       and  host  (IoT-NID).  MITM  attacks  include  ARP  spoofing
the standard local training, since the number of parameters in                    across datasets, with ICMP and DHCP spoofing inTON_IoT
these layers is small relative to the full model.                                 and DNS spoofing inEdge-IIoTset. Injection attacks cover
                                                                                  SQL, XSS (TON_IoT,Edge-IIoTset), and HTTP injection
                     IV.  EXPERIMENTALSETUP                                       (Edge-IIoTset).  Lastly,  malware  includes  brute-force  at-
   In  this  section,  we  describe  the  datasets  leveraged  for                temptsonHTTP(TON_IoT,Edge-IIoTset),telnet(IoT-NID),
the experiments (Sec.IV-A), along with the DL architecture                        FTP (TON_IoT), plus backdoors and ransomware inTON_IoT
employed (Sec.IV-B). Then, we introduce the FCIL scenarios                        andEdge-IIoTset. Concerning the physical testbed,IoT-NID
evaluated in this work (Sec.IV-D) and the metrics to quantify                     leverages smart devices and general-purpose hardware, while
NIDS capability to recognize and classify attacks (Sec.IV-E).                     TON_IoTandEdge-IIoTsetuse  hybrid  setups  with  both
                                                                                  physical and emulated devices.
A. Network Traffic of Cyber-attacks                                                  To ensure consistent labeling across all datasets, we apply
Datasets.For  the  experiments,  we  leverage3datasets  in-                       a rule-based preprocessing approach that refines label granu-
cluding  IoT  datasets,  collected  from2019onward—i.e.,                          larity. The labeling scheme follows a standardized format of
TON_IoT[47],IoT-NID[48], andEdge-IIoTset[49].                                     category-type(-subtype),  promoting  interpretability
   They  originally  includefive  categoriesof  attack  [49]:                     and  structure.  Defined  categories  includedos(denial-of-
(i)(Distributed) Denial of Service—(D)DoS—which includes                          service),infog(information gathering),mitm(man-in-the-
attacks aiming at causing service disruptions;(ii)Info Gath-                      middle),inject(injection),  andmalwr(malware)  [16].
ering,  which  covers  attacks  focused  on  obtaining  informa-                  Furthermore,  the  majority  classes  of  all  three  datasets  are
tion from the victim;(iii)Man-in-the-Middle—MITM—ad-                              subjected  to  random  sampling  to  achieve  a  biflow  number
dressing attacks involving the interception of communication;                     ranging from10k to100k. Notably, when analyzing the most
(iv)Injection, targeting the exploitation of vulnerabilities in                   and least represented attack classes, the imbalance ratios—
applications or systems to introduce malicious data or code;                      i.e.,  the  ratio  between  the  number  of  biflows  of  the  most
(v)Malware, covering uncategorized attacks.                                       populous  class  over  the  least  one—are400,700,  and340
   Within this category, varioussub-categoriescan be iden-                        forTON_IoT,Edge-IIoTset, andIoT-NID, respectively. This
tified  based  on  the  specific  type  of  attack  or  the  protocol             indicates a significant class imbalance—or skewness in the
```


### PDF page 8

[View original page, figures and tables](assets/page-008.png)

```text
IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. XX, NO. X, XXXX 2025                                                                                                               8

biflow  distribution—that  persists  even  after  undersampling,                   Table  II:  FCIL  scenarios  for  the  three  different  datasets,
although it has been partially mitigated. The distributions of                     detailed in the number ofK   old,K new, and clients.
the biflows, resulting from the relabeling procedure, for the                                 Scenario          Dataset|K          old|   |Knew|   N
three considered datasets are shown in Fig.2.           2                                                     TON_IoT          B+9A         2A        2
DL Input.In this work, we consider6per-packet characteris-                                       S1           IoT-NID          B+7A         2A        2
                                                                                                           Edge-IIoTset    B+11A        2A        2
tics, i.e. Payload Length (PL), Inter Arrival Time (IAT), Packet                                              TON_IoT          B+6A         5A        5
Direction (DIR), TCP Window Size (WIN), TCP Flags (FLG),                                         S2           IoT-NID          B+4A         5A        5
and Time To Live (TTL). To clarify, PL indicates the packet                                                Edge-IIoTset     B+8A         5A        5
length,  IAT  refers  to  the  time  interval  between  successive                           A: attack class;B: benign class.
packets, DIR denotes packet direction (0for downstream,1
for upstream), WIN represents the TCP window size (set to
0for UDP packets), FLG stands for the TCP flags converted                          all clients synchronize to a common model distributed by the
into a binary representation (ranging in[0,255]), and TTL                          federated server.
means how many routers (hops) a packet can pass through                               Additionally,  to  assess  the  effectiveness  of  our  solution
before being discarded. Fields such as IP addresses and ports                      across a distinct DL architecture, we evaluate a hybrid model
are deliberately excluded from the model’s training to prevent                     combining 2D-CNN and LSTM layers—denotedHYBRIDin
unwarranted bias [50]. In the following experiments, we use                        the following sections [54]. The network operates on the same
different feature sets:base—composed of PL, IAT, DIR, and                          input representation used by the 2D-CNN.
WIN—andextended—adding also FLG and TTL. The latter
features—i.e.,  TTL  and  FLG—have  been  shown  to  carry                         C. Upper Bound Approaches
valuable information for distinguishing between benign and                            To   recap,   FCIL   introduces   the   incremental   learning
malicious traffic [51], and we aim to evaluate their utility for                   paradigm into a federated setup. Therefore, to measure sep-
intrusion detection in a FCIL setting when focusing on the                         arately the performance loss introduced by each challenge—
IoT ecosystem.                                                                     i.e., decentralized data and need to update NIDS to cope with
   Last but not least, to supportearly detectionof malicious                       evolving threats—, we considertwo different upper bounds:
traffic, we extract features from the firstNpackets of each                        (i)Scratch, meaning that the model is trainedfrom-scratch
biflow. Prior work [50,52] has demonstrated that analyzing
per-packet  features  from  just  the  initial10packets  yields                    with all the data in acentralized fashionandno incremental
strong classification results, with only marginal improvements                     learning, and(ii)centralized CIL, which involves an incre-
when  incorporating  the  entire  biflow  [53].  Therefore,  time                  mental training performed in a centralized setup—i.e., the new
series data comprising the selected features from the first10                      classes of the considered scenario are added on a single client.
packets of each biflow are extracted. For shorter biflows, zero-                      WhileScratchuses all the data at a single point to perform
padding is applied to keep the sequence length consistent.                         training from scratch, centralized CIL assumes that each client
                                                                                   has access toD   mem for old classes along with the traffic data
B. DL model architecture                                                           for the new classes it intends to add.
   We  use  a  2D-CNN  architecture—originally  introduced
in [54] and widely adopted for both network Traffic Classi-                        D. FCIL scenarios
fication (TC) [50] and intrusion detection [15]—with mod-                             For the experiments, we define different federated incre-
ifications  to  support  incremental  learning.  Importantly,  our                 mental scenarios. In detail, a scenario is compactly referred
approach is model-agnostic and can be integrated with other                        to as⟨|K   old|+|K    new|,N⟩where|K              old|and|K       new|are the
DL architectures without requiring structural changes.                             number  of  old  and  new  classes,  respectively,  andNthe
   The2D-CNNis  composed  of  two  convolutional  layers                           number of clients in the federated network. Furthermore, in
(Conv2D) followed by pooling and normalization operations,                         both scenariosS                1/S2  we assume that each federated client
with a finalDenselayer providing the classifier output (i.e.,                      observesa(different)newattackatagiventimeandcooperates
a  confidence  vector).  The  architecture  has540k  trainable                     with other clients to incorporate all the attacks seen by the
parameters  and  is  fed  with  a  (matrix-arranged)  inputxof                     group (i.e. in such a case it holds|K         new|=N). Additionally,
packets×fieldsfor each biflow.                                                     all  clients  in  the  federated  network  adhere  to  a  common
   At  each  incremental  step,  the  backbone  of  the  network                   agreement on the number of communication rounds (R) to
remains  structurally  unchanged—i.e.,  no  architectural  mod-                    be performed. In each communication round, clients transmit
ifications are introduced—while the head is expanded with                          their locally trained models to the server, which aggregates
neurons for new attacks introduced that episode by federated                       them into a global model and redistributes it to all clients.
clients. Incremental training begins with the weights obtained                        The FCIL scenarios used for the experiments are reported in
from the previous incremental episode—i.e., the base model                         Tab.II, detailing for each dataset the number of old and new
weights (θ 0avg) for the initial one. At the end of each episode,                  classes and the number of clients in the federated network.

    2We leverage bidirectional flows (viz., biflows) as the traffic object. It     We consider federations of2and5clients, modeling realistic
encompasses all packets that share the same quintuple (src_ip,dst_ip,              cross-silosettingsinwhichgroupsofIoTdevices(e.g.,organi-
src_port,dst_port, andL4_proto), with interchangeablesrcanddst.                    zations or edge clusters) collaboratively train without sharing
```


### PDF page 9

[View original page, figures and tables](assets/page-009.png)

```text
IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. XX, NO. X, XXXX 2025                                                                                                               9


raw data, rather than large-scale cross-device FL. Across all
scenarios,K                old  always  includes  the  benign  class,  whereas
Knew contains only attack classes, reflecting the decentralized
emergence of new attacks.

E. Evaluation Metrics
   In this work, we evaluate federated and incremental NIDS
from  two  complementary  perspectives:  (i)  their  ability  to
classify  network  traffic  by  identifying  both  benign  device
activity and specific attack types, and (ii) their effectiveness
in distinguishing legitimate traffic from malicious traffic.
   To assess attack detection and recognition capabilities, we
leverageF1 Score(briefly, F1) as performance metric [34]. It
is computed as the harmonic mean of the per-class precision
and recall and then we obtain itsmacro versionby averaging
the per-class metrics over all the classes, namely
    F1 Score(θ,K) =                  1X2·Precision   i·Recall i
                             |K|  i∈K    Precisioni+Recall   i ,    (7)

whereKdenotes the generic class set andθa generic model
(learned from-scratch or in federated incremental fashion).
   To focus on NIDS detection capabilities, we use the partial
area under the curve (pAUC), which emphasizes performance
at low False Positive Rate (FPR). The pAUC is defined as:Z pu

                    pAUC =              TPR(fpr)dfpr                   (8)
                                   pℓ
wherep          ℓ = 0andp        u = 0.01, i.e., we compute the area under          Figure 3: FCIL performance onTON_IoTin theS                         1 scenario
the ROC—defined by True Positive Rate (TPR)—up to1%                                 with  the  base  feature  set.  Different  line  styles  distinguish
FPR, ensuring relevance for real-world NIDS conditions.                             approaches according to the mitigation strategies employed.
   To  obtain  insights  into  bothcatastrophic  forgettingand
intransigencephenomena  (due  to  the  incremental  learning
process), we break down both the considered metrics by the                          R={4,10,20,40,100,200}. Each client conducts a total of
subset of classesK           old,K new, andK      all, obtaining for a generic      200local training epochs, sharing its model with the server
metricXthe following sub-metrics:X                                   old,X new, andX      all.everyE= 200/Repochs. For each configuration, we test10
   To quantify a model’s gap from upper bound approaches,                           seeds, corresponding to10distinct (7÷3) train-test splits.
wedefinedropfromscratch(Drop-Scratch)anddropfrom                                    Results are shown as the average across the incremental runs
CIL(Drop-CIL) metrics measuring the difference in F1 and                            using10different seeds, each adding different new classes.
PAUC between FCIL NIDS and the upper bounds.                                           The rest framework leverages NumPy4 and Pandas5 for data
                                                                                    management  and  pre-processing,  PyTorch6  for  training  and
F. Implementation Details                                                           evaluating NIDS, and Matplotlib7 and Seaborn8 to plot results.
   In this section, we provide the implementation details for
the  FCIL  framework  used  in  this  work.  Specifically,  we                                          V.  EXPERIMENTALRESULTS
extend a Python-based framework—i.e.,FACIL                     3—to handle             We begin by analyzing performance in a few-client setting,
federated learning training. In detail, we devise a federated                       optimizing FCIL along two axes: feature set and FL algorithm
serverresponsibleforaggregatingthemodelsandcoordinating                             (Sec.V-A).  Then,  we  scale  to  a  larger  number  of  clients
and communicating with the clients during the local training                        (Sec.V-B),  compare  FCIL  withtraining  from  scratchand
procedure CIL. Additionally, we modify this framework to                            centralized  CIL  (Sec.V-C).  Furthermore,  we  evaluate  the
train multiple clients simultaneously, with each adding a new                       generalizability  of  our  FCIL  solution  across  different  DL
attack. The hyperparameters used for the training phase are the                     architectures (Sec.V-D) and examine the impact of IID attack
following:200epochs with patience of20, an initial learning                         data among clients (Sec.V-E). Lastly, we assess real-world
rate of0.1, a learning rate decay factor of3, and a minimum
learning rate of10  −4  . For memory-based CIL approaches,25                            4https://numpy.org/
biflows per eachK       old are selected [38]. In our experiments,                      5https://pandas.pydata.org/
we  explore  various  synchronization  frequencies  by  setting                         6https://pytorch.org/
                                                                                        7https://matplotlib.org/
    3https://github.com/mmasana/FACIL                                                   8https://seaborn.pydata.org/
```


### PDF page 10

[View original page, figures and tables](assets/page-010.png)

```text
IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. XX, NO. X, XXXX 2025                                                                                                             10

              Table III: FCIL performance onTON_IoTin theS                         1 scenario withexpanded feature set. Results are shown as the difference
              of F1 w.r.t. thebase feature set. Furthermore, they are broken down by the number of synchronization rounds performed and
              the set of classes.Green boldface textindicates improvement over the base set of features, whilered onerefers to decay in
              performance.Gray backgroundhighlights for each approach theRat which the best improvement over the base feature set is
              obtained, while thegreen oneshighlight the best approach and the bestRfor the considered setup.










              applicability,  focusing  on  cross-network  generalization  and                         improvement ingreen(resp. decay inred) obtained using the
              few-sample learning (Sec.V-F).                                                           expanded set of features over the base one.
                                                                                                           Generally speaking, performance onK    old  highly benefits
                                                                                                       from the use of the expanded set of features, withFT-Mem
              A. Few-client scenario                                                                   obtaining  the  highest  gain  w.r.t.  all  the  other  approaches.
                 Hereinafter, we evaluate FCIL performance in theS     1 sce-                          Notably, it improves at most by≈14%atR=20. Performance
              nario usingTON_IoT. Each paragraph answers a key research                                trends onK    all closely reflect those observed for old classes.
              question, stated as its title.                                                               On the other hand,K         new  presents more unstable trends.
                                                                                                       Specifically, FT-Mem, BiC,  andBiC                            +  demonstrate  a  gener-
              How  effective  is  FedAvg  with  a  base  set  of  features?                            ally positive trend across almost all synchronization values,
              In  response,  we  evaluate  all  CIL  methods  combined  with                           with improvements of up to 15%. In contrast,MEMENTOand
              FedAvg—usingbase feature setas input (viz., PL, IAT, DIR,                                MEMENTO+ experience a critical drop atR=40, losing16%
              and WIN). Results in Fig.3show that performance onK             all                      and8%, respectively, compared to the base feature set.
              closely mirrors that ofK   old, largely due to the imbalanced                                It is worth noting thatiCaRL+exhibits a distinctive trend.
              scenario with10base classes and only2new ones (attacks).                                 Its performance improves steadily by up to≈8%as the syn-
                 Performance trends vary across methods, depending on their                            chronization value increases toR=20, but beyond this point,
              CIL-focused mitigation strategies. Using only rehearsal (i.e.,                           it  experiences  a  sharp  decline,  dropping  to  around−18%.
              FT-Mem), F1 generally improves with more rounds, peaking at                              This  behavior  may  stem  from  theiCaRL+loss  becoming
              R= 200(i.e.,65%F1                         all). In contrast,iCaRL+(combining             less effective at higher synchronization intervals, potentially
              rehearsal and distillation) reaches its best performance earlier,                        causing forgetting or training instability.
              atR= 40(≈54%F1                       all/F1old and≈50%F1                 new). AsFT-Mem,
              iCaRL+struggles at lowRbut benefits from higher rounds.
                 CIL methods using all three mitigation strategiesbehave
              differently. Their performance onK            old drops asRincreases.
              ForK   new, outcomes depend on the bias correction strategy:
              (i)BiC—i.e.,  with  a  single  shared  correction  layer  for  all
              new classes—achieve peak F1  new scores atR= 20(≈56%)
              and (ii)BiC     + reaches its highest F1new (≈64%) atR=10.
              MEMENTObehaveslikeBiC,peakingatR= 40.ButMEMENTO                                          +
              follows  a  different  pattern:  performance  steadily  rises  with
              more rounds, reaching its best F1new (≈71%) atR=200.                                     What is the impact of different FL algorithms on perfor-
                                                                                                       mance?Lastly, we evaluate the performance of different FL
                                                                                                       algorithms, focusing on the top-2CIL approaches—i.e.,BiC                                        +
                                                                                                       andMEMENTO      +—and using the expanded feature set as input.
                                                                                                       Results of this analysis are shown in Fig.4.
                                                                                                           Notably, FedProxshows  significant  improvements  over
                                                                                                       FedAvgfor bothBiC                     + andMEMENTO      +, especially with a low
                                                                                                       number  of  synchronizations.  AsRincreases,  performance
                                                                                                       ofFedAvgandFedProxconverges  with  both  scoring  be-
  Takeaways.Old-class  performance  remains  stable                                                    tween74%and76%F1                               all forBiC     + andMEMENTO      +, respec-
  evenwithlimitedsynchronization,whereasnewclassesTakeaways.Expanded features lead to a performance    tively. Performance convergence is due to the improvement
  benefit from additional rounds to improve understand-improvement across all the synchronization round val-of  FedAvg  overFedProxonK                       old  with  higherR,  while
  ing. In addition, the proposed client-specific bias cor-ues  (except  foriCaRLDoes expanded feature set boost performance?+),  by  stabilizing  old  classesThen, weFedProxdelivers  better  performance  onK                   new,  especially
  rection strategy boostsperformance, but they can destabilize new-class learn-evaluate the impact of using anexpandedBiC           +/MEMENTO + effectiveness.feature set. ThewithMEMENTO       +. However, both approaches exhibit a declining
  Notably,  the  best  trade-off  is  obtained  byBiC    +  ating inMEMENTO/MEMENTO                    + at mid synchronizations. Inresults are reported in Tab.III, highlighting the performancetrend onK    old andK      new performance asRincreases.
CIL Appr.          R=4                 R=10                R=20                R=40               R=100             R=200R=10onK            all andK      old (≈69%summary,MEMENTO + obtains the best performance atF1            all,≈70%F1            old),
  R= 10(≈75%whileMEMENTO         + (second-best) reaches highest F1newF1old    F1new    F1all     F1old     F1new     F1all      F1old     F1new     F1all      F1old     F1new     F1all      F1old     F1new     F1all      F1old     F1new    F1allF1                    all,≈76%F1            old, and≈70%
FT-Mem    +8.78+10.85) atR=200F1new).(≈71%).+9.13+4.92+2.71+4.55 +13.80   +15.31   +14.05+10.38+8.53+10.07+11.81+9.07+11.35+10.97+3.47+9.72
iCaRL+      +2.91+2.92+2.91+7.17+5.18+6.84                       +8.21    +4.31     +7.56-17.52-13.09-16.78-6.71-5.74-6.55-17.55-13.20-16.82
BiC        +3.40+4.82+3.64+6.70-2.12+5.23+8.66+1.97+7.55                                     +8.90    +8.07    +8.76+8.51+4.43+7.83+8.13+3.24+7.32
MEMENTO+9.86-5.98+7.22                +10.52   +9.03    +10.27+9.89-1.63+7.97+8.84-16.33+4.64+10.12-2.39+8.03+8.98+1.35+7.71
BiC+           +3.15+0.32+2.68+6.57+1.42+5.71+8.40+2.49+7.41+7.42+7.48+7.43                                             +7.76    +5.88    +7.45+8.13+1.43+7.01
MEMENTO+    +9.53+4.68+8.72           +9.55    +5.52    +8.88    +9.98    +4.65     +9.09+8.45-8.17+5.68+10.46+2.83+9.19+8.92-3.82+6.79
```


### PDF page 11

[View original page, figures and tables](assets/page-011.png)

```text
IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. XX, NO. X, XXXX 2025                                                                                                             11

                                                                                                  Table IV: FCIL performance onTON_IoTin theS                         2 scenario
                                                                                                  using  theexpanded  feature  set.  For  each  combination,  the
                                                                                                  results highlight the best synchronization value, corresponding
                                                                                                  to the highest achieved F1all.

                                                                                                        FL Appr.     CIL Appr.    optimalR                         F1 Score [%]
                                                                                                                                                      Old       New        All

                                                                                                        FedAvg           BiC+               100           76.38    66.48    72.25MEMENTO+            20            79.64    64.32    73.25


                                                                                                        FedProx          BiC+                40            78.97    67.47    74.18MEMENTO+           100           79.05    68.10    74.49


                                                                                                        FedDyn           BiC+               200           79.28    65.13    73.38MEMENTO+           100           78.68    66.83    73.74


                                                                                                  edge acquisition, highlighting the need for frequent updates
                                                                                                  as client number and new classes grow.
                                                                                                     While no strict trends emerge, F1new  generally increases
                                                                                                  and  F1old  decreases  asRgrows.  Similar  toS          1, FedDyn
                                                                                                  performs notably worse atR={4,10}, whereasFedProx
                                                                                                  consistently leads at higherR, followed byFedDyn. Notably,
                                                                                                  FedProxpreserves old knowledge comparably toFedAvgand
                                                                                                  FedDyn,  while  achieving  better  F1             new,  making  it  the  best
                                                                                                  trade-off among the three.


           Figure 4: Comparison of different FL approaches forTON_IoT
           with expanded feature set in theS     1 scenario.


              On the other hand,FedDynshows lower performance for
           lowR,  while  obtaining  the  highest  F1  forR≥20.  This
           behavior can be attributed to the dynamic regularization in
           FedDyn,  which  corrects  for  client  drift  by  incorporating  a                     C. Wrap-up of results
           linear term related to the global model. Similar toFedAvg,
           asRincreases,FedDynshows improved F1                                    old, peaking at   In this section, we compare the performance of the top-
           R= 20, and F1       new, with best value occurring atR= 100                            performer FCIL approach against the upper boundScratch
           (resp.R= 20) forMEMENTO                       + (resp.BiC         +).                  baseline and centralized CIL training. Specifically, we evaluate
                                                                                                  performance in solving two relevant NIDS tasks: (i) bMD—
                                                                                                  i.e., distinguishing among legitimate and malicious traffic (all
                                                                                                  attacks as one class); (ii) AC—i.e., fine-grained classification
                                                                                                  of malicious traffic into different attack types. TableVsumma-
                                                                                                  rizestheresultsforthetwoscenarios,acrossallthreeevaluated
                                                                                                  datasets and the corresponding tasks discussed above.
                                                                                                     Considering  scenarioS              1,  the  best  FCIL  approach  (i.e.,
                                                                                                  MEMENTO+  withFedProxatR= 10)consistently  outper-
                                                                                                  formsthe best centralized CIL method (i.e.,MEMENTO) across
                                                                                                  bMD/AC tasks for bothTON_IoTandEdge-IIoTsetdatasets.
                                                                                                  However, despite these improvements, our solution still lags
           B. Many-client scenario                                                                behind theScratchbaseline, with performance gaps reaching
                                                                                                  up to3%in bMD and8%in AC. In contrast, for theIoT-NID
              In  this  section,  we  evaluate  FCIL  approaches  in  theS     2                  dataset, the CIL method slightly outperforms the FCIL one,
           scenario for theTON_IoTdataset with theexpanded feature                                showing improvements of+1%in PAUC            All and+2%in F1               all
           set.  TableIVreports  the  best  trade-off  achieved  for  each                        for AC. Moreover, the gap between our method andScratch
Takeaways.FCIL stability–plasticity is strongly in-combination of CIL and FL at specific values ofR. It is worthis even more pronounced forIoT-NID, with differences of up
fluenced  by  the  choice  of  FL  algorithm:FedProx
Takeaways.Many clients make FCIL’s process morenoting that having more clients with new classes makes thisto15%in AC. The ROC curves in Fig.5reveal a notable de-
supports rapid early integration,scenario more challenging, as more knowledge needs to beFedAvgtrails behindcline in TPR for the bMD task when compared to theScratch
challenging,  requiring  more  synchronizations  to  in-
across most settings, andFedDynintegrated into the model at each synchronization. Overall, aovertakes the oth-baseline—particularly at low false positive rates (FPR≤1%).
clude new knowledge. With a larger number of clients
ers only with many synchronization rounds. The bestfew synchronization rounds significantly hinder new knowl-This  drop  affects  both  CIL  and  FCIL  approaches,  which
(i.e.,S       2),MEMENTO  +  in  conjunction  withFedProx
trade-off of performance is reached byFedProxusing
results in the top-performing FCIL approch, achieving
MEMENTO+ atR=10, achieving≈79%F1                             all,≈80%
the highest F1all  atR= 100(≈75%), along with
F1old, and≈71%F1                 new.
≈80%F1           old and≈68%F1                 new.
```


### PDF page 12

[View original page, figures and tables](assets/page-012.png)

```text
IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. XX, NO. X, XXXX 2025                                                                                                             12

            Table V: Summary of performance for the best FCIL approach—in centralized and distributed fashion—andScratch, across
            scenarios (i.e.,S       1 andS      2) and datasets (i.e.,TON_IoT,IoT-NID, andEdge-IIoTset). Performance is reported as absolute
            value and drop w.r.t.Scratchand CIL approaches.Red(resp.green) text highlights the gap (resp. improvement) compared
            to upper bounds (i.e.,Scratchand CIL).

                 Scenario           Dataset                      Approach                                             bMD                                                                     AC
                                                                                     pAUCOld       pAUCNew       pAUCAll            F1 Old                F1 New                F1 All
                                                              Scratch                   99.05            99.48             99.13             83.68               92.61              85.30
                                   TON_IoT                    Best CIL                  92.67            90.53             92.28             76.80               70.85              75.72
                                                            Best FCIL*                  96.77            91.57             95.82             81.20               75.11              80.09
                                                     Drop-Scratch/CIL               2.28/-4.10        7.91/-1.04        3.31/-3.54        2.48/-4.40        17.50/-4.26          5.21/-4.37
                                                              Scratch                   99.96            99.96             99.96             76.19               87.12              77.87
                     S1        Edge-IIoTset                   Best CIL                  98.16            99.80             98.41             62.84               53.35              61.38
                                                            Best FCIL*                  98.70            98.65             98.69             68.49               74.78              69.46
                                                     Drop-Scratch/CIL               1.26/-0.54         1.31/1.15        1.27/-0.28        7.70/-5.65        12.34/-21.43         8.41/-8.08
                                                              Scratch                   96.27            96.68             96.36             98.48               98.51              98.48
                                   IoT-NID                    Best CIL                  93.45            92.12             93.15             89.54               71.39              85.51
                                                            Best FCIL*                  93.21            86.58             91.74             86.71               70.98              83.21
                                                     Drop-Scratch/CIL                3.06/0.24        10.10/5.54        4.62/1.41        11.77/2.83          27.53/0.41         15.27/2.30
                                                              Scratch                   99.08            99.19             99.13             83.32               87.69              85.30
                                   TON_IoT                    Best CIL                  92.59            91.64             92.16             68.24               77.69              72.57
                                                            Best FCIL†                  96.86            86.44             92.12             79.13               75.99              77.70
                                                     Drop-Scratch/CIL               2.22/-4.27        12.75/5.20        7.01/0.04        4.19/-10.89         11.70/1.70          7.60/-5.13
                                                              Scratch                   99.96            99.98             99.96             71.17               88.58              77.87
                     S2        Edge-IIoTset                   Best CIL                  94.65            90.64             93.11             53.43               70.35              59.94
                                                            Best FCIL†                  98.54            93.42             96.57             62.77               57.06              60.57
                                                     Drop-Scratch/CIL               1.42/-3.89        6.56/-2.78        3.39/-3.46        8.40/-9.34        31.52/13.29         17.30/-0.63
                                                              Scratch                   96.08            96.60             96.36             98.39               98.55              98.48
                                   IoT-NID                    Best CIL                  89.78            88.85             89.26             90.82               88.02              89.27
                                                            Best FCIL†                  94.12            87.22             90.29             88.79               78.77              83.22
                                                      Drop-Scratch/CIL              1.96/-4.34         9.38/1.63        6.07/-1.03        9.60/2.03          19.78/9.25         15.26/6.05
                Best CIL:MEMENTO;Best FCIL:MEMENTO                                         + +FedProxwithR=10(*);MEMENTO                                            + +FedProxwithR=100(†).

            exhibit  comparable  patterns.  The  degradation  is  especially                              Table VI: Multiclass misuse detection performance for the best
            severe forK    new, as reflected in the steeper decline of the ROC                            FCIL approach, obtained using theHYBRIDarchitecture [54],
            curves at low FPR values. Notably,MEMENTO +  consistently                                     compared by upper bounds—i.e.,Scratch, and CIL.
            outperformsMEMENTO, achieving higher TPR across bothK                                           old  Scenario               Approach                                mMD
            andK      all for equivalent FPR thresholds.                                                                                                      F1 Old     F1 New     F1 All
               In scenarioS              2, we observe a greater ability of the FCIL                                                     Scratch       85%        88%        86%
            approach  to  retain  previously  learned  knowledge  compared                                           S1                 Best CIL             75            60            72
            to  the  CIL  counterpart,  as  reflected  in  consistently  higher                                                           FCIL              80            72          79%
            performance  across  all  class-level  metrics.  However,  FCIL                                                    Drop-Scratch/CIL5/-5    16/-12  7/-7
            shows notable difficulty in incorporating new attack classes,                                                                Scratch         85            88            86
            with significant performance drops relative to CIL—reaching                                              S2                 Best CIL             63            52            59
                                                                                                                                          FCIL              78            60            70
            up to13%forEdge-IIoTsetin the AC task. Increasing the                                                              Drop-Scratch/CIL7/-12  28/-8   16/-11
            number of clients further degrades performance for both FCIL
            and CIL, while also amplifying the gap to theScratchbase-
            line. ForTON_IoTandEdge, the performance drops-IIoTset                                        D. Generalization across DL architectures
            nearly double, peaking at32%in DropF1          New  and17%in
            DropF1All. In contrast, forIoT-NID, the degradation remains                                       To assess the architecture-independent nature of our solu-
            comparable to that observed inS   1, with the DropF1New  in                                   tion, we evaluate the mMD performance forTON_IoTwhen
            the AC task even slightly lower than in the previous scenario.                                using theHYBRIDnetwork. TableVIshows results both for
                                                                                                          few-client (S 1) and many-client (S 2) scenarios, additionally
                                                                                                          comparing FCIL with upperbound approaches—namely, CIL
                                                                                                          andScratch.
                                                                                                              Results are consistent with those reported in Tab.Vfor
                                                                                                          TON_IoT.  Notably,  the  FCIL  approach  consistently  outper-
                                                                                                          forms centralized CIL when using theHYBRIDarchitecture.
                                                                                                          In theS     1 scenario, FCIL yields improvements of5%F1 on
Takeaways.FCIL  enables  robust  decentralized  in-                                                       previously seen classes and12%F1 on new classes, for an
cremental  learning  but  lags  behind  centralized  CIL                                                  overall gain of+7%in F1            all. Similarly, inS   2, FCIL better
andScratch. However, in both scenarios, FCIL out-                                                         retains  prior  knowledge  (+12%F1)  and  incorporates  new
performs CIL onTON_IoTandEdge-IIoTset. Con-                                                               classes more effectively (+8%F1), resulting in an average
versely,onIoT-NID,FCILstrugglesrelativetoCILand
Scratch, likely due to the presence of more difficult
or rarer attacks as new classes.
```


### PDF page 13

[View original page, figures and tables](assets/page-013.png)

```text
IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. XX, NO. X, XXXX 2025                                                                                                             13



















                                           (a)Scratch















                   (b)MEMENTO—CIL fashion                 (c)MEMENTO     +—FCIL fashion      Figure 6: Comparison of different FL approaches forTON_IoT
          Figure 5: ROC curves for (a)Scratch, (b)MEMENTO, and (c)                           on new IID data, alongside the best non-IID configuration.
          MEMENTO+ in theS     1 scenario on theTON_IoTdataset. Curves
          are averaged across all the seeds. The x-axis is displayedin a
          symlog scalefor improved visibility.                                               that  regularization-based  approaches  remain  beneficial  even
                                                                                             when client data are IID. Notably,FedDyngenerally achieves
          performance increase of11%F1 over centralized CIL.                                 the best or near-best performance for intermediate values of
             Despite  these advantages,  FCIL remains  below the  ideal                      R(i.e.,R= 20), highlighting its robustness in maintaining
          Scratchreference,  particularly  as  the  number  of  clients                      previously-learned knowledge, whileFedProxturns out to be
          grows. InS   1, it incurs a DropF1New of16%and a DropF1           Old              the best with lowR—namely,R=4.
          of5%, whereas inS             2 these losses rise to12%and28%, cor-                   Across  all  methods,  performance  on  theK     new  split  is
          responding to F1all reductions of7%and16%, respectively.                           systematically lower than onK    old, regardless ofR. This gap
                                                                                             reflects the inherent difficulty of CIL (even in the absence of
                                                                                             data heterogeneity) and suggests that catastrophic interference
                                                                                             with  newly-introduced  attacks  remains  a  central  challenge.
                                                                                             Nevertheless, moving from a non-IID to an IID setting yields
                                                                                             a substantial benefit for learning new classes, with the best IID
                                                                                             configuration—i.e.,FedProxatR=4—improvesperformance
                                                                                             onK    new by≈10%F1 compared to the best non-IID result—
          E. NIDS under new IID data                                                         i.e.,FedProxatR=10. This highlights the impact of data
             In  this  section,  we  evaluate  the  performance  of  FCIL                    distribution on plasticity and confirms that data homogeneity
          NIDS under an IID data, focusing on a few-client scenario                          significantly alleviates, though does not eliminate, the chal-
          where both clients encounter the same two novel attacks, but                       lenges associated with incremental class acquisition.

          with distinct biflows. Results of this analysis are reported in
          Fig.6for the different FL algorithms, along with the best
          FCIL configuration in the non-IID setup in which each client
          encounters a disjoint new attack, obtained in Sec.V-A.
             Similarly  to  the  non-IID  configuration,  best  results  are
          yielded also in the IID setup with lowR, then performance
          decreases  when  the  communication  rate  exceeds  a  given
          threshold. This behavior suggests that, under IID conditions,
          additional communication rounds provide diminishing returns                        F. NIDS in the Wild: Practical Challenges
Takeaways.In IID settings, FCIL performance peaksonce the models have sufficiently converged.
at low communication rounds, with diminishing returnsComparing FL approaches,FedProxandFedDynconsis-In  this  section,  we  analyze  some  practical  challenges  of
Takeaways.asRincreases;FedProxoutperform other FL algo-FCIL delivers consistent gains over cen-tently outperformFedAvgacross most settings. This indicatesNIDS when deployed in real-world scenarios: (i) capability
tralized CIL even when shifting to a different DL ar-rithms, and data homogeneity yields up to a10%F1
gain onK    new compared to the best non-IID setup, de-chitecture, confirming that the benefits of our approach
spitepersistentchallengesinincludingnewknowledge.generalize beyond a single model design.
```


### PDF page 14

[View original page, figures and tables](assets/page-014.png)

```text
IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. XX, NO. X, XXXX 2025                                                                                                             14

          Table VII: Binary detection capabilities inS   1 as PAUCAll for
          each⟨source,target⟩pair for the best FCIL solution and the
          best CIL one (in brackets). Green background highlights the
          pairs for whichsource=target.

              Source Dataset                                  Target Dataset
                                     TON_IoT         Edge-IIoTset         IoT-NID
                 TON_IoT          95.82(92.28)    74.90(69.42)     57.33(52.58)
              Edge-IIoTset54.88(52.79)               98.69(98.41)    60.60(60.92)
                  IoT-NID     51.97(55.59)     64.51(51.68)             91.74(93.15)

                                                                                                              (a) FCIL setup                    (b) CIL setup

          of generalizing across networks and (ii) ability to detect 0-
          day attacks with only a limited number of biflows available.
          How well do FCIL NIDS generalize across diverse net-
          works?In response, we separately evaluate the detection and
          classification performance of the best-performing FCIL model
          when deployed across different networks, and compare it with
          thebestCILmodelunderthesameconditions.Specifically,we
          report the results for the bMD task in Tab.VII, while Fig.7
          shows the AC performance when FCIL NIDS is trained on
          TON_IoTand tested with network traffic fromEdge-IIoTset                                             (c) FCIL setup                    (d) CIL setup
          andIoT-NID. Other combinations are not shown for brevity.                                        No   Classes                          No   Classes
              Specifically, Tab.VIIclearly shows a decline in detection                                                              10infog-scan-vuln
                                                                                                            1 dos-http11inject-http
          performance  when  the  NIDS  is  evaluated  on  a  different                                     2 dos-icmp12inject-sql
          network from the one it was trained on. Whileintra-dataset                                        3 dos-tcp    13inject-xss
                                                                                                            4 dos-tcp-ack14malwr-backd-tcp
          models achieve≥92%PAUC            All, performance drops signifi-                                 5 dos-tcp-syn15malwr-brutef-ftp
          cantly incross-datasetsetup—reaching at most75%PAUC                                        All    6 dos-udp    16malwr-brutef-http
                                                                                                            7 infog-scan-host17malwr-brutef-telnet
          (for⟨TON_IoT,Edge-IIoTset⟩), with other cases falling be-                                         8 infog-scan-os18malwr-ransomware
          low60%PAUC          All. In most of the combinations, the FCIL                                    9 infog-scan-port19mitm-arpspoof
          approach outperforms the CIL baseline in both intra-dataset                         Figure 7: Confusion matrices for NIDS trained onTON_IoT
          and  cross-dataset  scenarios,  likely  due  to  the  decentralized                 (sourcedataset)andevaluatedonEdge-IIoTset(toprow)and
          training and different client-specific data distributions.                          IoT-NID(bottom row) inS                  1. Gray-shaded rows and columns
              Similarly, the overall performance on the AC task remains                       indicate classes that are absent in the target or source dataset.
          unsatisfactory.  We  observedistinct  behavioral  patternsbe-
          tween  the  FCIL  and  CIL  NIDS  (see  Fig.7).  Specifically,
          when usingTON_IoTas the source dataset andEdge-IIoTset                              Can FCIL NIDS detect new 0-day attacks with just a few
          as the target, the FCIL setup shows a clear bias toward cer-                        samples?In this analysis, we assess the ability of a FCIL
          tain attack classes—such asdos-http,inject-sql, and                                 NIDS to incorporate new attacks while retaining knowledge
          malwr-backd-tcp—which are also the most frequent in                                 of previously learned ones, under a scenario characterized by
          the source dataset (Fig.7a). In contrast, the CIL setup exhibits                    ascarcity of new attack samples. Specifically, we constrain
          even more pronounced bias, particularly toward thedos-tcp                           the number of biflows available for each new attack class to
          andmalwr-brutef-httpclasses(Fig.7b).WhenIoT-NID                                     fixed values:15,25,50,100,200. For this analysis, we select
          is  used  as  the  target  dataset,  the  trend  reverses.  Both  ap-               for the few-shot training the seed that yields the best FCIL
          proaches  show  a  clear  prediction  bias  toward  specific  at-                   performance in the full-data setup (+inf). For each setting,
          tackclasses—suchasdos-tcp-syn,infog-scan-port,                                      samples are randomly drawn from the complete dataset corre-
          malwr-ransomware,  andmitm-arpspoof(Fig.7c).                                        sponding to that class. To ensure robustness and variability in
          The CIL setup displays a similar bias, though it is less pro-                       sample selection, each experiment is repeated10times, with
          nounced compared to the FCIL counterpart (Fig.7d). Similar                          results expressed as the average across the repetitions.
          results are observed across the other datasets and scenarios;                          Figure8compares the performance obtained by the best
          their confusion matrices are omitted for brevity.                                   FCILsolution—underfew-shotconditions(15to200samples)

                                                                                              and  full  data  (+inf)—andScratchfor  the  three  consid-
                                                                                              ered datasets in the few- and many-client scenarios. InS   1,
                                                                                              performance  onK    old  is  only  slightly  impacted  by  limited
                                                                                              sample  availability.  Interestingly,  performance  onK    new  is
Takeaways.FCIL NIDS generalize poorly across net-                                             often  comparable  to—or  even  better  than—the  full-sample
works. Notably, cross-dataset performance are biased                                          setting, except forEdge-IIoTset, where a notable drop is
toward majority attacks within the training set. Despite
decentralized training, detection performance remains
below65%PAUC.
```


### PDF page 15

[View original page, figures and tables](assets/page-015.png)

```text
IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. XX, NO. X, XXXX 2025                                                                                                             15


                                                                                                    In this work, we bridge the gap between CIL—enabling
                                                                                                 continuous learning—and FL—leveraging distributed data for
                                                                                                 training—by proposing FCIL, combining both approaches to
                                                                                                 design an adaptable, collaboratively trained NIDS. Our results
                                                                                                 show that FCIL methods effectively retain prior knowledge,
                                                                                                 especially leveraging TCP flags and time-to-live as input, but
                                                                                                 face challenges integrating new attacks.
                      (a)TON_IoT(S                        1)(b)TON_IoT(S                        2)  Overall,MEMENTO        +  combined with FedProx achieves the
                                                                                                 best  results  in  both  few-  and  many-client  settings.  In  the
                                                                                                 former,  fewer  synchronization  rounds  (R= 10)  suffice  for
                                                                                                 integrating new classes, while larger networks require more
                                                                                                 rounds(R=100)toaccommodatenewknowledge.Underthese
                                                                                                 conditions,MEMENTO                   + attains79%and75%F1                                all in the few-
                                                                                                 andmany-clientscenariosonTON_IoT,respectively.Generally
                       (c)IoT-NID(S                       1) (d)IoT-NID(S                       2)speaking, FCIL shows advantages over CIL in smaller net-
                                                                                                 works, though it does not reach the performance oftraining-
                                                                                                 from-scratch. As the number of clients grows, FCIL better
                                                                                                 preserves existing knowledge but faces increased difficulty in
                                                                                                 learning new attacks, leading to larger performance drops.
                                                                                                    In addition, we evaluate the NIDS in areal-world deploy-
                                                                                                 ment scenario, assessing both their (i) generalization capa-
                                                                                                 bilities and (ii) their ability to learn from limited samples.
                    (e)Edge-IIoTset(S                                    1)(f)Edge-IIoTset(S                                   2)Notably, deploying a NIDS in a different network environment
                                                                                                 significantly  reduces  its  detection  and  classification  perfor-
           Figure  8:  Performance  underfew-shot  conditions(ranging                            mance. However, the FCIL NIDS consistently outperforms its
           from15to200samples) andwith all samples(+∞) for the                                   CIL counterpart, demonstrating greater resilience to network
           best FCIL method andScratch, in both few-client and many-                             shifts. On the other hand, in few-shot settings, FCIL NIDS
           client scenarios using the best seed.                                                 achieves performance comparable to the full-data scenario—
                                                                                                 obtaining similar performance on old classes and sometimes
           observed  as  samples  decrease.  This  may  be  due  to  higher                      even outperforming it on new ones.
           sample variability or greater overlap in new attack fingerprints                         Ourfuture directionsinclude (a) enhancing CIL approaches
           for the selected seed inEdge-IIoTset.                                                 for  better  integration  of  new  attacks  in  federated  settings,
                                                                                                 (b)  advancing  personalization  to  balance  local  adaptation
              Similarly,  inS   2, K old  performance  remains  consistent                       with global knowledge, (c) strengthening privacy protections,
           between  the  two  different  settings.  However,  classification                     (d) reducing communication overhead, (e) improving robust-
           onK    new  improves  forIoT-NIDandEdge-IIoTset,  while                               ness against adversarial threats, and (f) including federated
           TON_IoTscores similarly to the full-sample setting.                                   domain-incremental learning.

                                                                                                                            ACKNOWLEDGMENT
                                                                                                    This work is partially supported by the “xInternet” Project–
                                                                                                 –funded by MUR—within the PRIN 2022 program (D.D.104-
                                                                                                 02/02/2022) and in part by the European Union under the
                                                                                                 Italian  National  Recovery  and  Resilience  Plan  (NRRP)  of
                                                                                                 NextGenerationEU,  partnership  on  “Telecommunications  of
                                       VI.  CONCLUSION                                           the  Future”  (PE00000001  -  program  “RESTART”).  This
              Guaranteeing  security  is  particularly  challenging  in  IoT                     manuscript reflects only the authors’ views and opinions and
           environments, where diverse devices continuously collect and                          the Ministry cannot be considered responsible for them.
           exchange  data.  In  this  domain,  ML-  and  DL-based  NIDS
           are crucial for defending against cyberattacks. However, the                                                          REFERENCES
           dynamic nature of IoT networks—characterized by frequent                               [1]“Microsoft    Digital    Defense    Report:    600    million    cyberattacks
           device churn and heterogeneity—leads to a broader and more                                  per     day     around     the     globe,”     https://news.microsoft.com/en-
           exposed attack surface. New attacks may emerge frequently,                                  cee/2024/11/29/microsoft-digital-defense-report-600-million-
           making  NIDS  models  quickly  outdated  and  requiring  the                                cyberattacks-per-day-around-the-globe/, 2024, accessed: 2025-06-12.
                                                                                                  [2]Cisco       Systems,       “Detecting       zero-days       with       SnortML,”
           ability to learn new threats incrementally. Furthermore, attack                             https://www.cisco.com/c/en/us/products/collateral/security/firewalls/
           traffic can vary significantly across networks. While sharing                               detecting-zero-days-with-snortml-wp.html,  2024,  accessed:  2025-05-
Takeaways.FCIL NIDS can learn new0-day attacksdata across deployments could improve detection coverage,22.
                                                                                                  [3]M.  Antonakakis,  T.  April,  M.  Bailey,  M.  Bernhard,  E.  Bursztein,
from very few samples while preserving prior knowl-privacy concerns make this approach impractical.    J. Cochran, Z. Durumeric, J. A. Halderman, L. Invernizzi, M. Kallitsis
edge,  often  improving  new-class  recognition  across
client scenarios—e.g.,TON_IoTandIoT-NIDinS                                                                     1 or
IoT-NIDandEdge-IIoTsetinS                                                    2.
```


### PDF page 16

[View original page, figures and tables](assets/page-016.png)

```text
IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. XX, NO. X, XXXX 2025                                                                                                             16



      et  al.,  “Understanding  the  Mirai  botnet,”  in26th  USENIX  security                     [26]Z.  Jin,  J.  Zhou,  B.  Li,  X.  Wu,  and  C.  Duan,  “FL-IIDS:  A  novel
      symposium (USENIX Security 17), 2017, pp. 1093–1110.                                                federated learning-based incremental intrusion detection system,”Future
 [4]B. Zhao, S. Ji, J. Xu, Y. Tian, Q. Wei, Q. Wang, C. Lyu, X. Zhang,                                    Generation Computer Systems, vol. 151, pp. 57–70, 2024.
      C.  Lin,  J.  Wuet  al.,  “A  large-scale  empirical  analysis  of  the  vul-                [27]J. Mao, Z. Wei, B. Li, R. Zhang, and L. Song, “Towards Ever-Evolution
      nerabilities introduced by third-party components in IoT firmware,” in                              Network Threats: A Hierarchical Federated Class-Incremental Learning
      Proceedings of the 31st ACM SIGSOFT International Symposium on                                      Approach  for  Network  Intrusion  Detection  in  IIoT,”IEEE  Internet
      Software Testing and Analysis, 2022, pp. 442–454.                                                   Things J., 2024.
 [5]G.Apruzzese,L.Pajola,andM.Conti,“Thecross-evaluationofmachine                                  [28]Z. Zhang, Y. Zhang, H. Li, S. Liu, W. Chen, Z. Zhang, and L. Tang,
      learning-based network intrusion detection systems,”IEEE Trans. Netw.                               “Federated continual representation learning for evolutionary distributed
      Service Manag., vol. 19, no. 4, pp. 5152–5169, 2022.                                                intrusion detection in Industrial Internet of Things,”Engineering Appli-
 [6]S. Agrawal, S. Sarkar, O. Aouedi, G. Yenduri, K. Piamrat, M. Alazab,                                  cations of Artificial Intelligence, vol. 135, p. 108826, 2024.
      S. Bhattacharya, P. K. R. Maddikunta, and T. R. Gadekallu, “Federated                        [29]N.  H.  Quyen,  N.  V.  Hoang,  P.  T.  Duy,  and  V.-H.  Pham,  “FI-IDS:
      learning for intrusion detection system: Concepts, challenges and future                            A  Federated  Incremental  Learning  Approach  for  Intrusion  Detection
      directions,”Computer Communications, vol. 195, pp. 346–361, 2022.                                   System,” inIEEE International Conference on Advanced Technologies
 [7]E. M. Campos, P. F. Saura, A. González-Vidal, J. L. Hernández-Ramos,                                  for Communications (ATC), 2024, pp. 432–437.
      J.  B.  Bernabé,  G.  Baldini,  and  A.  Skarmeta,  “Evaluating  Federated                   [30]H. A. Tran, H. T. T. Binh, and A. Mellouk, “Federated learning for
      Learning  for  intrusion  detection  in  Internet  of  Things:  Review  and                         network  traffic  classification:  A  knowledge  consolidation  approach,”
      challenges,”Computer Networks, vol. 203, p. 108661, 2022.                                           IEEE Trans. Netw. Sci. Eng., 2025.
 [8]H. Zhang, J. Ye, W. Huang, X. Liu, and J. Gu, “Survey of federated                             [31]M. Masana, X. Liu, B. Twardowski, M. Menta, A. D. Bagdanov, and
      learning  in  intrusion  detection,”Journal  of  Parallel  and  Distributed                         J. Van De Weijer, “Class-incremental learning: survey and performance
      Computing, p. 104976, 2024.                                                                         evaluation on image classification,”IEEE Trans. Pattern Anal. Mach.
 [9]M.  Data  and  M.  Aritsugi,  “An  incremental  learning  algorithm  on                               Intell., vol. 45, no. 5, pp. 5513–5533, 2022.
      imbalanced data for network intrusion detection systems,” in10th ACM                         [32]Q. Li, Z. Wen, Z. Wu, S. Hu, N. Wang, Y. Li, X. Liu, and B. He, “A
      International Conference on Computer and Communications Manage-                                     survey on federated learning systems: Vision, hype and reality for data
      ment (ICCCM), 2022, pp. 191–199.                                                                    privacy and protection,”IEEE Trans. Knowl. Data Eng., vol. 35, no. 4,
[10]C. Oikonomou, I. Iliopoulos, D. Ioannidis, and D. Tzovaras, “A multi-                                 pp. 3347–3366, 2021.
      class intrusion detection system based on continual learning,” inIEEE                        [33]P. Kairouz, H. B. McMahan, B. Avent, A. Bellet, M. Bennis, A. N.
      International Conference on Cyber Security and Resilience (CSR), 2023,                              Bhagoji, K. Bonawitz, Z. Charles, G. Cormode, R. Cummingset al.,
      pp. 86–91.                                                                                          “Advances and open problems in federated learning,”Foundations and
[11]Z. Song, Z. Zhao, F. Zhang, G. Xiong, G. Cheng, X. Zhao, S. Guo, and                                  trends® in machine learning, vol. 14, no. 1–2, pp. 1–210, 2021.
      B. Chen, “I  2RNN: An Incremental and Interpretable Recurrent Neural                         [34]G. Bovenzi, A. Nascita, L. Yang, A. Finamore, G. Aceto, D. Ciuonzo,
      Network for Encrypted Traffic Classification,”IEEE Trans. Depend. Sec.                              A. Pescapé, and D. Rossi, “Benchmarking class incremental learning in
      Comput., 2023.                                                                                      deep learning traffic classification,”IEEE Trans. Netw. Service Manag.,
[12]L.  Du,  Z.  Gu,  Y.  Wang,  L.  Wang,  and  Y.  Jia,  “A  few-shot  class-                           vol. 21, no. 1, pp. 51–69, 2023.
      incremental  learning  method  for  network  intrusion  detection,”IEEE                      [35]G. Bovenzi, L. Yang, A. Finamore, G. Aceto, D. Ciuonzo, A. Pescapè,
      Trans. Netw. Service Manag., vol. 21, no. 2, pp. 2389–2401, 2023.                                   and D. Rossi, “A first look at class incremental learning in deep learning
[13]Y. Wang and S. Cao, “A Two-Stage Class Incremental Learning Ap-                                       mobile traffic classification,” inProc. IFIP Traffic Monitoring Analysis
      proach for Network Intrusion Detection,” inIEEE Global Communica-                                   (TMA), 2021.
      tions Conference (GLOBECOM), 2024, pp. 2353–2358.                                            [36]Y. Wu, Y. Chen, L. Wang, Y. Ye, Z. Liu, Y. Guo, and Y. Fu, “Large scale
[14]X. Xu, X. Zhang, Q. Zhang, Y. Wang, B. Adebisi, T. Ohtsuki, H. Sari,                                  incremental  learning,”  inProc.  IEEE/CVF  Conference  on  Computer
      and G. Gui, “Advancing malware detection in network traffic with self-                              Vision and Pattern Recognition (CVPR), 2019, pp. 374–382.
      paced class incremental learning,”IEEE Internet Things J., 2024.                             [37]R. Carillo, F. Cerasuolo, G. Bovenzi, D. Ciuonzo, and Pescapè, “Ex-
[15]F. Cerasuolo, G. Bovenzi, D. Ciuonzo, and A. Pescapè, “Attack-adaptive                                plainable Federated Class Incremental Learning for Encrypted Network
      network  intrusion  detection  systems  for  IoT  networks  through  class                          Traffic Classification,”Computer Networks, vol. 245, p. 110374, 2025.
      incremental learning,”Computer Networks, p. 111228, 2025.                                    [38]F. Cerasuolo, A. Nascita, G. Bovenzi, G. Aceto, D. Ciuonzo, A. Pescapè,
[16]——, “Adaptable, incremental, and explainable network intrusion de-                                    and D. Rossi, “MEMENTO: A novel approach for class incremental
      tection  systems  for  internet  of  things,”Engineering  Applications  of                          learning of encrypted traffic,”Computer Networks, vol. 245, p. 110374,
      Artificial Intelligence, vol. 144, p. 110143, 2025.                                                 2024.
[17]V. Rey, P. M. S. Sánchez, A. H. Celdrán, and G. Bovet, “Federated                              [39]D.-W. Zhou, Q.-W. Wang, Z.-H. Qi, H.-J. Ye, D.-C. Zhan, and Z. Liu,
      learning for malware detection in IoT devices,”Computer Networks,                                   “Class-incremental  learning:  A  survey,”IEEE  Trans.  Pattern  Anal.
      vol. 204, p. 108693, 2022.                                                                          Mach. Intell., 2024.
[18]Z. Tang, H. Hu, and C. Xu, “A federated learning method for network                            [40]J. Zhang, F. Li, F. Ye, and H. Wu, “Autonomous unknown-application
      intrusion detection,”Concurrency and Computation: Practice and Ex-                                  filtering  and  labeling  for  dl-based  traffic  classifier  update,”  inIEEE
      perience, vol. 34, no. 10, p. e6812, 2022.                                                          Conference on Computer Communications (INFOCOM), 2020, pp. 397–
[19]O.  Friha,  M.  A.  Ferrag,  L.  Shu,  L.  Maglaras,  K.-K.  R.  Choo,  and                           405.
      M. Nafaa, “FELIDS: Federated learning-based intrusion detection sys-                         [41]H.  Chen,  S.  Huang,  D.  Zhang,  M.  Xiao,  M.  Skoglund,  and  H.  V.
      tem for agricultural Internet of Things,”Journal of Parallel and Dis-                               Poor, “Federated learning over wireless iot networks with optimized
      tributed Computing, vol. 165, pp. 17–31, 2022.                                                      communication and resources,”IEEE Internet Things J., vol. 9, no. 17,
[20]J. Li, X. Tong, J. Liu, and L. Cheng, “An efficient federated learning                                pp. 16592–16605, 2022.
      system for network intrusion detection,”IEEE Syst. J., vol. 17, no. 2,                       [42]X. Gao, X. Yang, H. Yu, Y. Kang, and T. Li, “Fedprok: Trustworthy
      pp. 2455–2464, 2023.                                                                                federated class-incremental learning via prototypical feature knowledge
[21]M.  J.  Idrissi,  H.  Alami,  A.  El  Mahdaouy,  A.  El  Mekki,  S.  Oualil,                          transfer,”  inProc.  IEEE/CVF  Conference  on  Computer  Vision  and
      Z. Yartaoui, and I. Berrada, “Fed-anids: Federated learning for anomaly-                            Pattern Recognition (CVPR), 2024, pp. 4205–4214.
      based network intrusion detection systems,”Expert Systems with Appli-                        [43]J. Dong, H. Li, Y. Cong, G. Sun, Y. Zhang, and L. Van Gool, “No
      cations, vol. 234, p. 121000, 2023.                                                                 one left behind: Real-world federated class-incremental learning,”IEEE
[22]M. Bhavsar, Y. Bekele, K. Roy, J. Kelly, and D. Limbrick, “FL-IDS:                                    Trans. Pattern Anal. Mach. Intell., 2023.
      Federated learning-based intrusion detection system using edge devices                       [44]B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. A. y Arcas,
      for transportation IoT,”IEEE Access, 2024.                                                          “Communication-efficient learning of deep networks from decentralized
[23]M.-y. Zhu, Z. Chen, K.-f. Chen, N. Lv, and Y. Zhong, “Attention-based                                 data,” inArtificial intelligence and statistics.   PMLR, 2017, pp. 1273–
      federated incremental learning for traffic classification in the Internet of                        1282.
      Things,”Computer Communications, vol. 185, pp. 168–175, 2022.                                [45]T. Li, A. K. Sahu, M. Zaheer, M. Sanjabi, A. Talwalkar, and V. Smith,
[24]R. R. dos Santos, E. K. Viegas, A. O. Santin, and P. Tedeschi, “Fed-                                  “Federated  optimization  in  heterogeneous  networks,”Proceedings  of
      erated learning for reliable model updates in network-based intrusion                               Machine learning and systems, vol. 2, pp. 429–450, 2020.
      detection,”Computers & Security, vol. 133, p. 103413, 2023.                                  [46]D. A. E. Acar, Y. Zhao, R. M. Navarro, M. Mattina, P. N. Whatmough,
[25]D. Jin, S. Chen, H. He, X. Jiang, S. Cheng, and J. Yang, “Federated                                   and V. Saligrama, “Federated learning based on dynamic regularization,”
      incrementallearningbasedevolvableintrusiondetectionsystemforzero-                                   arXiv preprint arXiv:2111.04263, 2021.
      day attacks,”IEEE Netw., vol. 37, no. 1, pp. 125–132, 2023.                                  [47]T.  M.  Booij,  I.  Chiscop,  E.  Meeuwissen,  N.  Moustafa,  and  F.  T.
```


### PDF page 17

[View original page, figures and tables](assets/page-017.png)

```text
IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. XX, NO. X, XXXX 2025                                                                                                             17



      den  Hartog,  “Ton_IoT:  The  role  of  heterogeneity  and  the  need  for                    [51]W. John and S. Tafvelin, “Analysis of Internet backbone traffic and
      standardization of features and attack types in IoT network intrusion                                header anomalies observed,” inProc. 7th ACM SIGCOMM Conference
      datasets,”IEEE Internet Things J., 2021.                                                             on Internet Measurement (IMC), 2007, pp. 111–116.
[48]H.  Kang,  D.  H.  Ahn,  G.  M.  Lee,  J.  D.  Yoo,  K.  H.  Park,  and                         [52]L. Peng, B. Yang, and Y. Chen, “Effective packet number for early stage
      H. K. Kim, “IoT network intrusion dataset,” 2019. [Online]. Available:                               internet traffic identification,”Neurocomputing, vol. 156, pp. 252–267,
      https://dx.doi.org/10.21227/q70p-q449                                                                2015.
[49]M. A. Ferrag, O. Friha, D. Hamouda, L. Maglaras, and H. Janicke,                                [53]M.  Wang,  N.  Yang,  and  N.  Weng,  “Exploring  the  Impact  of  Early
      “Edge-IIoTset: A new comprehensive realistic cyber security dataset of                               Detection on DL-Based NIDSs Models,” inIEEE 14th Annual Ubiq-
      IoT and IIoT applications for centralized and federated learning,”IEEE                               uitous Computing, Electronics & Mobile Communication Conference
      Access, vol. 10, pp. 40281–40306, 2022.                                                              (UEMCON), 10 2023, pp. 0684–0691.
[50]G.  Aceto,  D.  Ciuonzo,  A.  Montieri,  and  A.  Pescapé,  “Mobile  en-                        [54]M. Lopez-Martin, B. Carro, A. Sanchez-Esguevillas, and J. Lloret, “Net-
      crypted  traffic  classification  using  deep  learning:  Experimental  eval-                        work traffic classifier with convolutional and recurrent neural networks
      uation,  lessons  learned,  and  challenges,”IEEE  Trans.  Netw.  Service                            for Internet of Things,”IEEE Access, vol. 5, pp. 18042–18050, 2017.
      Manag., vol. 16, no. 2, pp. 445–458, 2019.
```
