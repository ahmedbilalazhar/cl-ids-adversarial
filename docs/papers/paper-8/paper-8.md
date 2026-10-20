# Attack-adaptive network intrusion detection systems for IoT networks through class incremental learning

**Authors:** Francesco Cerasuolo; Giampaolo Bovenzi; Domenico Ciuonzo; Antonio Pescapè

**Publication:** Computer Networks 263, 111228 (2025), Elsevier.

**Publication DOI:** https://doi.org/10.1016/j.comnet.2025.111228

**Verified free PDF:** https://domenicociuonzo.wordpress.com/wp-content/uploads/2025/03/comnet25_cil_ids.pdf

**Downloaded version:** Public author manuscript submitted 17 March 2025; matched to the published May 2025 Computer Networks article through DOI metadata and the author publication list. Numerical findings refer to this complete 22-page author version.

**Qualification:** Q1, COMPUTER SCIENCE, INFORMATION SYSTEMS; 2024 JIF quartiles, June 2025 JCR release.

**Integrity:** 22 pages; 1,733,201 bytes; SHA-256 `028f64a52ce50919ac17bf4ca3a7ddc6268394bb2b1e879e8aabb1933fa381cb`.

## Reading and extraction note

The complete PDF is authoritative. Automatic page text can lose two-column ordering, ligatures, equation syntax and table alignment. Original-page PNGs preserve figures, tables and equations. See [the selection audit](../phase2-selection-audit.md) for synthesis.

## Full manuscript text


### PDF page 1

[View original page, figures and tables](assets/page-001.png)

```text
Attack-Adaptive Network Intrusion Detection Systems
                               for IoT Networks through Class Incremental Learning

                             Francesco Cerasuolo, Giampaolo Bovenzi, Domenico Ciuonzo, Antonio Pescap`e

                                                            University of Napoli Federico II, Italy





Abstract
   The advent of the Internet of Things (IoT) has ushered in an era of unprecedented connectivity and convenience, enabling
everyday objects to gather and share data autonomously, revolutionizing industries, and improving quality of life. However, this
interconnectedlandscapeposescybersecuritychallenges,astheexpandedattacksurfaceexposesvulnerabilitiesripeforexploitation
by malicious actors. The surge in network attacks targeting IoT devices underscores the urgency for robust and evolving security
measures.  Class Incremental Learning (CIL) emerges as a dynamic strategy to address these challenges, empowering Machine
Learning (ML) and Deep Learning (DL) models to adapt to evolving threats while maintaining proficiency in detecting known
ones. In the context of IoT security, characterized by the constant emergence of novel attack types, CIL offers apowerfulmeans
to enhance Network Intrusion Detection Systems (NIDS) resilience and network security. This paper aims to investigate how CIL
methods can support the evolution of NIDS within IoT networks(      i) by evaluating both attack detection and classification tasks—
optimizinghyperparametersassociatedwiththeincrementalupdateortothetrafficinputdefinition—and( ii)byaddressingalsokey
researchquestionsrelatedtoreal-worldNIDSchallenges—suchastheexplainabilityofdecisions,therobustnesstoperturbationof
traffic inputs, and scenarios with a scarcity of new-attack samples.Leveraging               4 recently-collected and comprehensive IoT attack
datasets, the study aims to evaluate the effectiveness of CIL techniques in classifying 0-day attacks.


1. Introduction                                                                  to tackle the challenge at hand. This approach empowers Ma-
   The rise of the Internet of Things (IoT) has marked an era                    chine Learning (ML) and Deep Learning (DL) models to learn
characterized by unparalleled connectivity and convenience,                      and adapt to new types of attacks while retaining proficiency
wherein everyday objects can now autonomously collect and                        in detecting previously encountered threats [7].  In the realm
exchange data [1].  This paradigm shift has revolutionized in-                   ofIoTsecurity—characterizedbythecontinuousemergenceof
dustries, improved our overall quality of life, and opened up                    novel attack types, diversity and low-cost nature of devices—
new frontiers in technology.                                                     CILcanprovetobeapowerfulmeanstoenhancetheresilience
   Nevertheless, this interconnected ecosystem introduces sev-                   of Network Intrusion Detection Systems (NIDS) and bolster
eral cybersecurity challenges by expanding the attack surface                    the security of network environments.  Specifically, CIL elim-
and exposing vulnerabilities that malicious actors are eager to                  inates the need to train classifiers from scratch when new at-
exploit. Alongside the rapid proliferation of IoT devices, there                 tack types occur, making them adaptive and thereby reducing
has been a noticeable surge in network attacks specifically tar-                 thetimerequiredtodeployafully-operationalNIDScapableof
geting these devices [2, 3].  Cyber attackers acknowledge the                    distinguishing among all attacks.
potential for causing disruptions,  stealing data,  and gaining                     Accordingly, the contribution of this paper is twofold:  (i)
unauthorized access that arises from vulnerabilities in IoT sys-                 we investigate the incremental update of NIDS through CIL,
tems. Consequently, the need for robust and adaptable security                   with the aim of including knowledge of 0-day attacks, and (ii)
measures in the IoT landscape has never been more empha-                         we analyze incremental NIDSs when facing real-world chal-
sized [4].  This challenge is exacerbated by the ever-evolving                   lenges.  These challenges include opaque decision-making in
nature of the cybersecurity landscape, where defenders contin-                   ML/DL architectures impeding their widespread adoption, as-
uously fortify digital fortresses, while adversaries relentlessly                sessment of the degree of robustness in the presence of slightly
search for vulnerabilities to exploit, even generating new kinds                 different network deployments or mutated/unforeseen network
of attacks (viz. 0-day attacks) [5, 6].                                          conditions, scarce availability of samples for 0-day attacks to
   In  response  to  this  dynamic  scenario,  Class  Incremental                be included requiring significant resources and specialized (or
Learning (CIL) emerges as a dynamic and adaptive strategy                        emulated) configurations.
                                                                                    Specifically,weaddress the following       research questions
    Email addresses: francesco.cerasuolo@unina.it (Francesco                     associated with NIDS challenges in real-world scenarios:
Cerasuolo),giampaolo.bovenzi@unina.it (Giampaolo Bovenzi),                          • Q1: Cantheknowledgeofanexisting(IoT-focused)NIDS
domenico.ciuonzo@unina.it (Domenico Ciuonzo),pescape@unina.it
(Antonio Pescap`e)                                                                     beextendedtonewattacktrafficclassesbyleveraging(ad-

Preprint submitted to Computer Networks                                                                                                                                                                        March 17, 2025
```


### PDF page 2

[View original page, figures and tables](assets/page-002.png)

```text
vanced) CIL approaches?  How are attack detection and                                       Table 1: List of the acronyms used in the manuscript.
      classification capabilities separately affected?                                            Acronym     Definition
   •  Q2: Can the optimization of hyperparameters, either as-                                     IoT                Internet of Things
      sociatedtotheincrementalupdate(i.e.memorysize)orto                                          CIL               Class Incremental Learning
                                                                                                  ML               Machine Learning
      the traffic input definition (i.e. number of packets and se-                                DL                Deep Learning
      lected packet fields as features) improve the performance                                   NIDS            Network Intrusion Detection Systems
      of an extended NIDS?                                                                        AC                Attack Classification
                                                                                                  bMD             Binary Misuse Detection
   •  Q3:   Can  the  explainability  of  decisions  motivate  the                                FSCIL           Few-Shot Class Incremental Learning
                                                                                                  MetaL           Meta-Learning
      decision-process of incremental models?                                                     MG               Model Growth
                                                                                                  FT                 Fine-Tuning
   •  Q4:  Can the robustness to perturbation of inputs be af-                                    AD                Anomaly Detection
      fectedbytheCILapproachleveragedtoextendtheNIDS?                                             TO                Traffic Object
                                                                                                  CNN             Convolutional Neural Network
   •  Q5: How do CIL approaches behave when there is (rea-                                        LSTM           Long Short-Term Memory
      sonably) scarcity of new attack samples?                                                    SOTA            State-of-the-art
                                                                                                  BL                Baselines
                                                                                                  SHAP           SHapley Additive exPlanations
To address these questions, we leverage 4 of the most up-to-                                      IG                 Integrated Gradients
date and comprehensive IoT attack datasets currently avail-                                       BA                Balanced Accuracy
able, namely IoT-23 [8], TON-IoT [9], IoT-NID [10], and                                           ROC             Receiver Operating Characteristic
Edge-IIoT [11], ensuring robust evaluation when investigat-                                       AUC             Area Under Curve
                                                                                                  PAUC           Partial Area Under Curve
ing how CIL techniques perform in addressing the challenges                                       FPR              False Positive Rate
of classifying 0-day attacks.                                                                     PL                 Network-layer Packet Length
   The rest of the paper is organized as follows. In the upcom-                                   IAT               Inter-Arrival Time
ing sections, we first delve into the literature related to the ap-                               WIN             TCP Window Size
                                                                                                  DIR               Packet Direction
plication of CIL approaches to attack classification (AC) and                                     TTL              Time-To-Live
binary misuse detection (bMD) tasks (Sec. 2). Following that,                                     FLG              TCP Flags
we provide a comprehensive overview of our research method-
ologies (Sec. 3) and outline our experimental setup (Sec. 4).
Then, we present our empirical findings (Sec. 5) and evaluate                           Furthermore,  considered works deal with different incre-
theproposedCIL-enabledNIDSmethodologyinthecontextof                                  mental tasks (columns “Incremental Task”).  Notably, a few
real-world challenges (Sec. 6). Last, we delve into discussions                      of them address the challenge of Few-Shot Class Incremental
regarding the broader implications and future directions of our                      Learning (FSCIL) [7, 19, 21] by expanding the classifier while
research(Sec.7). Forthesakeofreadability,theacronymsused                             considering constraints of a limited number of samples. They
in this manuscript are summarized in Tab. 1.                                         analyze a different number of samples (viz. shots), specifically
                                                                                     {3,6,10,15} in [7], {2,5,10} in [19], {5} in [21].  Conversely,
2. Related Work                                                                      the others tackle the incremental task without any constraint.
                                                                                     Regarding the family of incremental approaches employed,
   In this section, we discuss literature concerning CIL in the                      for FSCIL tasks they employ meta-learning (MetaL) [7, 19],
domain of NIDS, with a specific focus on the challenge of                            model-growth (MG) [7] or fine-tuning (FT) [21]. However, for
adapting existing classifiers/detectors to accommodate emerg-                        CIL, they leverage only MG [22], or FT approaches [23].
ing types of attacks or patterns of anomalies. CIL offers an ad-                        In terms of the tasks addressed (column “Task”), the ma-
vantagebycontinuouslyexpandingmodelstoaddressevolving                                jority focus on distinguishing benign and malicious traffic in
threats while preserving previously acquired knowledge.  Our                         anunsupervised[12]—viz.  anomalydetection(AD)—orsuper-
literature review identified various approaches in this context,                     visedfashion[13,14,15,16,17]—viz.  binarymisusedetection
listed in Tab. 2 and categorized along different relevant axes.                      (bMD)—while the remaining ones deal with classifying (in a
   While all the works under consideration explore incremen-                         flat fashion) between benign and all the attack classes—viz.
tal learning setups, only our preliminary conference paper [23]                      multiclass misuse detection (mMD).
explores the adoption of incremental approaches to IoT traf-                            As for traffic object (column “TO”), all the considered work
fic (column “IoT”). Specifically (column “Dataset”), most of                         leverage biflows(viz. bi-directional flows) except for [19] con-
them leverage the KDDCUP99 dataset [12, 13, 14, 15, 16] or its                       sidering(unidirectional)flowsand[22]employingsessions. In-
enhanced version, NSL-KDD [7, 17]. Conversely, others employ                         terestingly, the majority of reviewed studies propose non-Deep
CIC-IDS2017 [18, 19, 20, 21, 22] dataset and or its improved                         Learning (DL) solutions (column “DL”). These solutions en-
version CIC-IDS2018 [21].  In contrast to the aforementioned                         compassarangeoftechniques(column“ML/DLApproach”),
works, only Cerasuolo et al. [23] relies on the IoT-23 dataset,                      including clustering [12, 13], tree-based algorithms [14, 18],
a recently collected dataset encompassing traffic from real IoT                      support vector machines [15, 16, 17, 18],  k-nearest neigh-
devices.                                                                             bor [14, 16, 7],  Bayesian classifiers [7],  and ensemble ap-
                                                                                 2
```


### PDF page 3

[View original page, figures and tables](assets/page-003.png)

```text
Table 2: State-of-the-art works in chronological order leveraging CIL to incrementally extend NIDS.






















            proaches[18]. Conversely,otherexaminedworksleverageDL-                                     sign (column “Rob.”).
            based approaches [7, 19, 20, 21, 22, 23].   Specifically, they                             Positioning of our work. In this study, our primary goal is to
            employ convolutional neural networks (CNNs) [19, 23], trans-                               evaluate how CIL solutions enhance the adaptability of NIDS
            formers [21], Long Short-Term Memory (LSTM) [22], oruse                                    forIoTnetworks,enablingswiftresponsestoemergingandpre-
            DL feature extractors with clustering algorithms [20].                                     viously unknown attacks (viz. 0-day).  Accordingly, our study
               Crucially,  most of these studies primarily concentrate on                              diverges from most state-of-the-art (SOTA) works as we focus
            post-mortem detection—i.e. they do not perform   early detec-                              onIoT devicetraffic, encompassing4IoT datasetswith diverse
            tion (column “Early Detection”).   Specifically, these works                               devices and attack scenarios [8, 9, 10, 11].
            leverage mainly statistics computed on the entire traffic object                              Equally important, we employ cutting-edge CIL solutions to
            or,inthecaseofDialloandPatras[20],theyalsoemployheader                                     handle the complex challenges associated with NIDS design
            fields taken fromall its packets. Conversely, other works only                             which can be virtually applied to any DL model. Specifically,
            use fields extracted by packets header or payload as model in-                             the considered CIL solutions belong to the fine-tuning family,
            putwithoutrelyingonanysummarizingfeature(column“Raw                                        duetothehighercomplexityinvolvedwithusingmodel-growth
            Input”). The latter corpus of literature is usually matched with                           and meta-learning approaches which may impair their applica-
            an early detection, as only the fields of the firstNp packets are                          tion to the IoT ecosystem [24, 25].
            used.                                                                                         Furthermore,instarkcontrasttoallrevisedstudies,oureval-
               Anotheraspecttoconsideristhedepthofanalysiscarriedout                                   uationfocusesonhowCILsolutionsempoweringNIDSdesign
            by each study.  Only a few works investigate how to optimize                               affect both AC and bMD tasks. The aim is to assess the effect
            hyperparameters for enhanced performance (column “Hyp.”),                                  of the incremental training process on NIDS (attack) detection
            suchasexaminingthevariationsinSVMkernels[15]orscruti-                                      and classificationcapabilities in a separate fashion.
            nizingtheinfluenceofadjustingthenumberofpreviousepisode                                       Also, as opposed to SOTA (focusing only on some model-
            samples during the update phase [17]. Other studies delve into                             dependent [15] or limited [17] aspects), we undertake a com-
            improving the explainability of incremental classifiers (column                            prehensive examination adjusting critical parameters through-
            “XAI”) only in a partial fashion.   Specifically, they mainly                              out the incremental process to optimize the performance of the
            leverage a single technique to determine the contribution to the                           adaptive NIDS.
            performance of input or part of the design. For instance, Cera-                               Last but not least, we investigate real-world challenges for
            suolo et al. [23] employ a feature-attribution technique (viz.                             incremental NIDS including (a) explainability, (b) robustness,
            DeepSHAP)topinpointtheunderlyingcausesbehindmisclas-                                       and (c) few-samples availability. Specifically, we leverage dif-
            sifications of specific class samples by the incremental clas-                             ferent input attribution techniques (i.e. SHAP and Integrated
            sifier, while Xu et al. [19] and Du et al. [21] conduct abla-                              Gradients)toexplainthereasonbehindpredictionsandweeval-
            tion studies to gauge the effectiveness of individual compo-                               uate the accordance between them, we analyze the robustness
            nents within their proposed solutions.  Conversely, Song et al.                            oftheincrementalmodel’sperformanceinpresenceofdatacor-
            [22] propose an explainable-by-design architecture and a cor-                              ruption,andweevaluateperformancewhenonlyafew-samples
            respondingad-hocexplainabilitymethodisinvestigatedtoana-                                   of 0-day attack are available for training models.  Hence, our
            lyzefeatureimportanceforattackclassification,definingafea-                                 study represents a first attempt from the standpoint of (b) and
            ture ranking. Finally, up to our knowledge, no work deals with                             a first general methodology for (a)—since [22] focused on
            robustness analysis of CIL methods in the context of NIDS de-                              explainability-by-design of a very specific DL model.
 Paper                          Year    IoT            Dataset                             IncrementalTask                          Task        TO    DL      EarlyRawML/DLAnalyses
                                                         CIL    FSCIL    #Shots(K)    Appr.Family                                                                                         Hyp.    XAI    Rob.3DetectionInputApproach

 Burbecketal.[12]       2007    ✗        KDDCUP99         ✓       ✗         –            –            AD        B     ✗       ✗         ✗      Clustering    #      #      #
 Zhongetal.[13]              2008   ✗           KDDCUP99        ✓      ✗             –                 –                bMD         B    ✗       ✗        ✗         Clustering  #  #  #
 Yuetal.[14]            2009    ✗        KDDCUP99         ✓       ✗         –            –           bMD        B     ✗       ✗         ✗     K-Means,DT     #      #      #
 Yietal.[15]                   2011   ✗           KDDCUP99        ✓      ✗             –                 –               mMD         B    ✗       ✗        ✗            SVM   G#  #  #
 Xuetal.[16]            2017    ✗        KDDCUP99         ✓       ✗         –            –           mMD        B     ✗       ✗         ✗      kNN-SVM       #      #      #
 Constantinidesetal.[17]    2019   ✗            NLS-KDD        ✓      ✗             –                 –               mMD         B    ✗       ✗        ✗            SVM   G#  #  #
 Wangetal.[7]           2021    ✗         NLS-KDD         ✗       ✓      3,6,10,15     MetaL         mMD        B     ✓       ✗         ✗     DNN,KNN,       #      G#     #
                                                                                        MG                                                     SVM,BC
 Dataetal.[18]                2022   ✗         CIC-IDS2017      ✓      ✗             –                 –               mMD         B    ✗       ✗        ✗       AdaBoost,HT #  #  #
 Xuetal.[19]            2022    ✗       CIC-IDS2017       ✗       ✓       2,5,10       MetaL         mMD        F     ✓       ✓         ✓       1D-CNN       #      G#     #
 Dialloetal.[20]              2023   ✗         CIC-IDS2017      ✓      ✗             –                 –            bMD,mMD     B    ✓       ✗        ✓         Clustering  #  #  #
 Duetal.[21]            2023    ✗       CIC-IDS2017       ✗       ✓         5            FT        bMD,mMD      B     ✓       ✓         ✓      Transformer   #      G#     #
                                        CIC-IDS2018
 Songetal.[22]               2023   ✗         CIC-IDS2017      ✓      ✗             –                MG              mMD         S    ✓      ✓       ✓           LSTM   #  G#  #
 Cerasuoloetal.[23]     2023    ✓         IoT-23          ✓       ✗         –            FT        bMD,mMD      B     ✓       ✓         ✓       2D-CNN       #      G#     #

 Thispaper                     2024   ✓     IoT-23,Edge-IIoT,TON-IoT,IoT-NID    ✓      ✓        5,25,50,100,200            FT            bMD,AC       B    ✓      ✓       ✓         2D-CNN

IncrementalTask: ClassIncrementalLearning(CIL),Few-ShotClassIncrementalLearning(FSCIL);IncrementalApproachFamily: Meta-Learning(MetaL),Model-Growth(MG),Fine-Tuning(FT);Task: Attack
Classification(AC),AnomalyDetection(AD),binaryMisuseDetection(bMD),multi-classMisuseDetection(mMD);TrafficObject(TO):Biflow(B),Flow(F),Session(S);ML/DLApproach: DecisionTree(DT),
SupportVectorMachine(SVM),k-NearestNeighbour(k-NN),DeepNeuralNetwork(DNN),BayesianClassifier(BC),HoeffdingTree(HT),ConvolutionalNeuralNetwork(CNN),LongShort-TermMemory(LSTM);
Hyper-parameters(Hyp.);eXplainableAI(XAI);Robustness(Rob.); performed,G#partiallyperformed,#notperformed;✓present,✗lacking.
```


### PDF page 4

[View original page, figures and tables](assets/page-004.png)

```text
Figure 1: Overview of the process of incremental training of an Attack-Adaptive NIDS,including performed tasks and real-world challenges addressed.

Table 3: CIL approaches belonging to the fine-tuning family adopted in this work.  They are categorized into Baselines (BL) and SOTA. For each approach, we
reported the paper introducing that approach, employed mitigation strategies, and optimizable hyperparameters.


                        Approach         Year                                          Mitigation Strategy                                               Hyper Params
                                                 Rehearsal     Distillation     Regularization     Bias Correction
                        FT[26]           2020         #              #                #                   #                      –
                        FT-Mem [24]       2023          #       #        #                         mem-size
                        LwF[27]          2017         #                                                   #                 λdist,λreg,T
                        EWC[28]            2017          #                #                     mem-size,λreg
                        EEIL [29]        2018                                         #                   G#               mem-size,T
                        BiC[30]            2019                  #                                mem-size,T
                        LUCIR[31]        2019                                                             G#           mem-size,k,ρbase,σ
                        iCaRL+ [32]     2021                  #        #                         mem-size

                   Hyper Params: Memory size (mem-size), Temperature (T);  present,G# partial/form of,# lacking;


3. Methodology                                                                     logits have a size equal the number of classes to discriminate
   Inthefollowingsection,webeginbypresentingfundamental                            from.   The logits are finally passed through a softmax layer
conceptsconcerningCIL(Sec.3.1). Then,wedelveintoSOTA                               (i.e. o→ p= softmax(o)) to provide a probabilistic confidence
incremental approaches employed to design NIDS (Sec. 3.2).                         vector passociated with the classification task.
Next,wedelineatethemethodologyutilizedfortheXAIanaly-                                 CIL methods fall into three families based on how they
ses conducted (Sec. 3.3), as well as for the robustness analyses                   expand the model and which model parts they update [33]:
(Sec. 3.4) and few-shot scenarios (Sec. 3.5).  An overview of                      (i) fine-tuning expands the model head and updates the en-
theincrementaltrainingprocess(andcorrespondingreal-world                           tire model with new and optionally old data;(       ii) fixed-rep-
evaluation) for an attack-adaptive NIDS is depicted in Fig. 1.                     resentation expands the model head, and freezes parts of the
                                                                                   pre-trained model (viz. backbone and/or old head), definitively
3.1. Background on CIL                                                             training the non-frozen parts;(        iii) model-growth maintains the
                                                                                   base model and adds a new model (or trainable layers) for the
   CIL represents a learning paradigm employed to update pre-                      new classes, combining their outputs for classification.
trainedmodels,enablingthemtoincorporatenewclasseswhile                                CIL encounters challenges such as catastrophic forgetting
retaining previously acquired knowledge. This approach elim-                       (loss of old knowledge) and intransigence (inability to learn
inates the need for retraining models from scratch and proves                      new classes). To address these issues, mitigation strategies are
particularly advantageous in dynamic environments [24].                            introduced,includingrehearsal(storingasmallpartofolddata,
   In detail, the CIL problem involves introducing new classes                     with herding being the most adopted sampling strategy [34]),
(Cnew) leveraging associated data (Dnew) into a model initially                    implicit-  (namely  distillation  [27])  or  explicit-regularization
trained on samples from old classes (Dold) to expand its clas-                     (minimizing updates to backbone parameters [28]), and bias
sification capabilities across the overall set of classes (Call =                  correction (addressing model bias towards new classes [30]).
Cold∪Cnew). This process leverages existing model parameters                          The training process is guided by a composite loss function,
(θ∗), new classes data, and optionally withholds some old data                     represented as
asmemory(Dmem). Incontrasttotraining-from-scratch(which                                       L= λclass · Lclass+λreg · Lreg+λdist · Ldist         (1)
usesD = Dnew⊕Dold), the resulting model update leverages
D=Dnew⊕Dmem as the training set, withDmem≪Dold.                                    This composite loss aims to simultaneously encourage model
   Typically, a DL model consists of a backbone, responsible                       stability, through the regularization terms (i.e.,Lreg andLdist),
for feature extraction (i.e.  x →  φ(x)) from the traffic input                    and plasticity, via the classification term (i.e.,Lclass).The goal
x, and a head, dealing with classification and providing log-                      is to strike a balance between learning new information and re-
its (i.e. the model output φ →  o(φ)).  It is worth noting that                    taining previously acquired knowledge.
                                                                                4
```


### PDF page 5

[View original page, figures and tables](assets/page-005.png)

```text
Insummary,CILprovestobeavaluableparadigmforadapt-                            updates.  It employs a two-term loss function: Lclass, akin to
ing models to new data in evolving environments, eliminating                   LwF’s approach but applied only to new classes, and a regular-
the need for time-consuming retraining from scratch.  In our                   ization term Lreg that weighs parameter importance based on
specificcontext,ourobjectiveistoenhanceaclassifierinitially                    theFIM.Thisregularizationbalancesadaptationtonewclasses
trained on a set of existing attacks and benign traffic (viz. old              while preserving old class parameters.  In its original formu-
classes) by incorporating new knowledge about 0-day attacks                    lation, EWC computes the FIM post-training solely fromDnew.
(viz. new classes).                                                            However,integratingamemory,assuggestedby[33],enhances
                                                                               performance, especially in CIL scenarios. Therefore, the algo-
3.2. CIL approaches                                                            rithmfirstupdatesthemodelandthen,aspost-processingsteps
  In this section, we outline the CIL approaches investigated                  (i.e. needed for subsequent updates), it computes the Fisher in-
in this work.  Remarkably, all the methods utilized belong to                  formation matrix and herding selection.
the fine-tuningfamily [33], being recognized for achieving the                 EEIL—End-to-End  Incremental  Learning    [29]:   this  ap-
highest performance in the mobile traffic classification con-                  proachaimstoenhanceiCaRL’sdesign[34]byintegratingend-
text [24] and shown to be promising in preliminary attempts                    to-end learning mechanisms that concurrently update the clas-
towards adaptive NIDS design [23]. Notably, we opt not to ex-                  sifier and the feature representation. EEIL utilizes a dual-term
plore model-growth approaches due to their limited scalability                 loss function comprising a classification loss term (Lclass) and
withincreasingincrementsandhighermemorydemands,mak-                            a distillation term (Ldist), similar to that of LwF.   Addition-
ing them unsuitable for deployment in the IoT context.                         ally, EEIL introduces balanced fine-tuning to mitigate the in-
  Initially,weintroducetwobaseline(BL)methods,namelyFT                         herentimbalancebetweennewsamplesandoldclassexemplars
andFT-Mem, representing the most straightforward approaches.                   (|Dnew| ≫ |Dmem|). Following the model update, EEIL selects
Subsequently, we delve into six more advanced methods that                     a subset of Dnew equal in size to the memory and conducts a
integrate one or more mitigation strategies recalled in Sec. 3.1.              secondary fine-tuning step using the same procedure outlined
Table 3 offers a comprehensive overview of the considered ap-                  previously but with a reduced learning rate. As a result, EEIL
proaches, along with an indication of the employed mitigation                  operatesafollows. First,distillationprobabilitiesarecollected,
strategies for each.                                                           then the model update is triggered.  The model update is then
FT—Fine-Tuning:   it represents the most straightforward solu-                 refined via balanced fine-tuning.  Finally, herding selection is
tionformodelupdates,involvingtheupdateoftheentiremodel                         performed to build memory for next updates.
with only the samples of new classes (viz.Dnew).                               LUCIR—LearningaUnifiedClassifierIncrementallyviaRe-
FT-Mem—Fine-TuningwithMemory:   avariationoftheprevi-                          balancing[31]: thismethodintroducesasophisticatedregular-
ousapproach,FT-Memwithholdsasubsetofoldclassessamples                          ization approach, surpassing EWC’s focus on the backbone and
as a memory. These retained samples are reintroduced into the                  EEIL’streatmentofmagnitudebias. Thelossfunctionincludes
modelduringtheincrementaltrainingtocopewithcatastrophic                        Lclass,akintoEEIL’s,andtwoadditionalterms,Ldist andLreg.
forgetting (viz.D=Dnew⊕Dmem).                                                  Specifically,Ldist isweightedbyρbase·p|Cnew|/|Cold|(ρbase be-
                                                                               ing a dataset-specific parameter) while for the other two terms
LwF—Learning Without Forgetting   [27]:  this is a memory-                     λreg=λclass=1. First,Lclass isappliedtoallclasses(old+new)
free approach (viz.D = Dnew) that pioneers the application of                  with softmax computed on cosine-distance normalized scores
KnowledgeDistillation(KD)inincrementallearningscenarios.                       oi(x) ≜ cd(ζi,φ(x)), where ζi is the ith class embedding2 and
KDimprovesgeneralizationperformancebytransferringexper-                        cd(v1,v2) ≜ ⟨v1,v2⟩/(∥v1∥∥v2∥) is the cosine distance.   The
tise from a pre-trained model (viz. teacher) to a target network               model head of LUCIR projects the feature vector φ(x) into a
(viz.student)[35]. Specifically,LwFemploysathree-termloss:                     cosinespace(∈ [−1,1]),potentiallyalleviatingmagnitudebias.
a classification term (Lclass) dedicated to incorporating new                  A learned parameter η automatically scales all           oi(x)’s to com-
classes,distillation(Ldist)andregularization(Lreg)termstore-                   pensateformagnitudedifferencesacrossupdates. Additionally,
tainpreviouslyacquiredknowledgeofoldclasses. Thebalance                        theless-forgetlossdistillationLdist,computedwiththeoldand
among classification, distillation, and regularization losses is               updated feature vectors (φ∗(x) and φ(x), respectively), is used
upheld by adjusting hyperparameters λdist and λreg1, which are                 to constrain the latent space.  This loss term is computed as
specifically applied to the distillation and regularization terms,             Ldist = Px∈D(1−cd(φ∗(x),φ(x))).  Furthermore, a marginal-
respectively.                                                                  ranklossreinforcestheseparationbetweenoldandnewclasses,
EWC—Elastic Weights Consolidation   [28]: this approach re-                    contrasting class embeddings’ reactions when activated by old
liesontheFisherinformationmatrix(FIM)diagonal,indicating                       class exemplars x∈Dmem—the cosine-normalized score of the
the sensitivity of each parameter’s loss derivative near a mini-               true old class ¯ogt(x) should be higher than the same measure
mum. Highvaluesimplysignificantparameterinfluenceonthe                         appliedtoanyofthenewclasses,i.e. ¯oi(x),∀i∈Cnew. Thisloss
loss, necessitating stabilization to prevent catastrophic forget-              compares     ogt(x) against the top-k measures from new classes,
ting.  EWC uses a single head, freezing old parameters during                  Tk,addingapenaltyonlyifthedifferenceissmallerthanamar-
                                                                               ginσ:Lreg =Px∈DmemnPi∈Tk max 0,σ− ¯ogt(x)+ ¯oi(x) o.


   1InLwF,λreg was consistently set as a fixed parameter at 5·10−4.               2LUCIRhead uses embeddings rather than a linear layer head.

                                                                            5
```


### PDF page 6

[View original page, figures and tables](assets/page-006.png)

```text
iCaRL+—Incremental    Classifier    and    Representation                       Integrated Gradients. IG is based on the input baseline con-
Learning Plus [32]: this approach is an adapted and improved                    cept,derivedfromhumantendenciestoattributeeffectsthrough
version of iCaRL [34] for the TC domain. iCaRL+ includes a                      counterfactualintuition. Itimplicitlycomparesaspecificeffect,
rehearsal strategy (via herding selection), leverages an output                 like a classifier decision, with its absence, achieved by model-
layer  that  dynamically  expands  and  activates  through  the                 ing the absence using a single baseline input.
softmax function (in contrast to the Nearest Mean Classifier                       Inessence,IGquantifiestheimportanceofeachinput(em)in
employed by iCaRL), and employs a loss function comprising                      altering confidence relative to the same class with the baseline
classification and distillation (KD) loss terms,  each equally                  input. It achieves this by considering a straight-line path from
weighted (λclass=λdist=1).                                                      the baseline (x′) to the input (x), computing gradients at all
BiC—Bias Correction   [30]:  this method tackles the bias to-                   points along this path, and then cumulating them.
ward new classes by introducing an additional layer to correct                     Lastly,  we normalize SHAP/IG local explanations (eem  =
the bias of the model head output.This bias correction layer                    em/PMm=1em) and then aggregate them across diverse samples
is parameterized by two factors α and β.   The correction is                    obtaining global explanations [39].  In this work, we leverage
specifically applied to the logits of new classes (onew), while                 SHAP and IG to explain confidence levels associated with pre-
thelogits ofoldclasses (oold)remain unchanged. Precisely,the                    dicted classes (i.e. legitimate traffic or specific attacks).
correction transforms onew in ¯o(x) = α ·  onew(x)+ β· 1. The                      Furthermore,giventheabsenceofastandardizedXAIframe-
incremental training process for this approach then operates as                 work and the potential for feature-attribution methods to yield
follows.  First, to reduce forgetting, the model is updated us-                 varied explanations, leveraging diverse techniques and quanti-
ing a composite loss function with classification and KD terms                  fyingtheircoherenceiscrucial foraccurate interpretation[40].
(weighted byλclass =|Cnew|/|Call| andλdist = 1−λclass, respec-
tively). Then,theadditionallayeristrainedwithasmalldataset                      CoherenceofExplanations. Weevaluatethecoherenceofdif-
todeterminethetwocorrectionparametersbyfreezingboththe                          ferent explanation techniques through two different per-sample
model components (viz. backbone and head). Specifically, the                    metrics, namely Top5Ratio and Avg.Rel. [41].   The former
dataset to train the correction layer encompasses a balanced                    measures the similarity between explanations considering the
number of per-class samples, obtained as ⌈P%· Nold⌉, where                      top-5 most important features for different explanation meth-
Nold represents the number of old samples for each class be-                    ods. It is computed as follows:
longingtoCold. Intheoriginalformulationandpreviousworks,
P is set to 10% of per-class memory samples.                                             Top5Ratio= |Top5(SHAP(x))∩Top5(IG(x))|5                        ,      (2)
For  completeness,  in  our  analysis,  we  consider  the  model                where SHAP(x) (resp. IG(x)) refers to the explanation ob-
trainedfromscratchwithalldatafrombotholdandnewclasses                           tained by DeepSHAP (resp. IG). The Top5Ratio metric is then
astheperformanceupperbound. Henceforth,wewillrefertoit                          normalized within (0,100)%, where 100% signifies full agree-
asScratch.                                                                      ment among XAI techniques whereas 0% indicates total dis-

3.3. XAI Methodology                                                            agreement.
                                                                                   Conversely, the Avg.Rel. quantifies the overall difference in
  To  interpret  complex  DL  architectures  after  incremental                 inputimportanceattributedtodifferentmethodstothesamein-
training, we leverage input-attribution methods providing a lo-                 put biflow. It is computed as:
cal explanation (viz. per-sample explanation) to elucidate the
model behavior in the neighborhood of each instance (x) after                                                    ZX
model training (viz. post-hoc analysis).  Per-sample explana-                                  Avg.Rel.= 1Z         |SHAPi(x)−IGi(x)|,              (3)
tions from local methods are here aggregated to obtain global                                                   i=1
explanations.  In this work, we leverage SHapley Additive ex-                   where Z denotes the number of input components (i.e. the size
Planations (SHAP) [36] and Integrated Gradients (IG) [37].                      of x). Accordingly, a smaller Avg.Rel. suggests greater consis-
SHAP.Shapleyvalues,originatingfromcooperativegamethe-                           tency, indicating their similarity, while a larger value implies
ory, determine each player’s contributionm to the overall pay-                  lower reliability.
offv(P) of the entire coalition P.  In this method, subsets of                     Then, we obtain a global version of these two metrics aver-
cooperating players S ⊂ P are assessed to gauge the impact of                   aging each across all considered samples.
addingorremovingplayermonthetotalpayoffv(S). Whenin-                            3.4. Robustness to Perturbed Inputs
terpreting DL-based models, input data serve as players in the
cooperativegame,andtheDLarchitecture’soutputf(x)actsas                             In this work, we analyze the robustness of the incremen-
the payofffunction.                                                             tal and Scratch models to input perturbations, generally de-
  In this work, we employ DeepSHAP [38], a rapid approxi-                       scribed as x→ ∆(x). Specifically, we assess whether and how
mation algorithm, to gauge the significance of inputs in deter-                 much traffic input perturbations seen only during the inference
mining the class (i.e. SHAP values). Specifically, we interpret                 stage affect NIDS detection and classification performance.
SHAP values (em) as the importance of inputs in determining                     We purposefully refrain from delving into adversarial pertur-
confidence levels for class labeling.                                           bations [42], as they tend to be model-specific and are crafted
                                                                             6
```


### PDF page 7

[View original page, figures and tables](assets/page-007.png)

```text
based on the responses of a particular model.   Instead,  we                   4. Experimental Setup
opt to employ more universally-applicable techniques, lever-                      In this section, we present a thorough overview of the ex-
aging general primitives ∆(·) to manipulate input data [43].                   perimental setup utilized in our analyses. Specifically, Sec. 4.1
This broader approach allows us to explore perturbation meth-                  presents the metrics employed for evaluating CIL approaches
ods that are not tied to specific models and can potentially                   inthecontextofNIDSdesign. Thecharacteristicsofleveraged
have wider applicability across various domains and contexts.                  IoT traffic datasets are discussed in Sec. 4.2, while Sec. 4.3 de-
Equally important, we focus on input manipulations employed                    lineatesthemodelarchitecturetakenintoconsideration. Lastly,
which mirror real-world network scenarios.                                     Sec. 4.4 introduces the relevant CIL setups and scenarios.
  Specifically, we consider perturbations emulating modifica-
tion in network conditions: (i) jittering that mimic fluctuations              4.1. Evaluation metrics
in IAT between consecutive packets
          IATjit≜hiat1   ···    iatNpi+hϵ1   ···   ϵNpi,                          In this study, we employ the F1 Score (briefly F1), a com-
                                                                               monly used metric for assessing DL model performance and
where ϵi (i = 1,...,NP) are different random values while NP                   evaluating the classification capabilitiesof a CIL model. This
denotesthenumberofpacketsconsideredintheinput;(ii)time-                        metricrepresentstheharmonicmeanofprecisionandrecallfor
out emulating network overloading and packet loss leading to                   eachclass,withthemacroF1beingthearithmeticaverageover
TCP packet retransmission; (iii) flippingthat alter the direction              all classes, expressed as:
of the communication—i.e. modifies the DIR of packets from                                                   X    2·Precisioni·Recalli
upstream to downstream and vice-versa; (iv) slicing simulating                              F1(θ,C)=  1|C|         Precisioni+Recalli  ,            (4)
an interruption of communication, hence NIDS can focus only                                                   i∈C
on the first half of the biflow segment for decisions:                         where C denotes a generic set of classes, and θ represents a
    Bslicing≜ hpkt1   ···    pkt Np   i+hpkt Np              pktNpi,           genericmodel,learnedeitherfromscratchorinanincremental

                                    2           2 +1   ···
where B and pkt denote the biflow and packet, respectively,                    manner.
while  pktthepacketmaskedwithpaddingvaluesforeachinput                            Given that the F1, influenced by precision and recall, may
field.                                                                         obscurethemodel’sbehavior,thisstudyalsoincludesBalanced
  It is worth noticing that the first two perturbations are ran-               Accuracy (BA) to enhance evaluation and provide a clearer un-
dom, while the latter two are deterministic. Hence, in the for-                derstanding of whether catastrophic forgetting or intransigence
mercase,the(random)perturbationprocessreliesonsomedis-                         is occurring [44]. This metric is defined as follows:
tributional parameters. Specifically, the random values for jit-                                                       X
tering perturbation are drawn from a Gaussian distribution de-                                       BA(θ,C)=  1|C|        Recalli.                        (5)
                                                                                                                       i∈C
fined by the pair (µ,σ), whereas the timeout is triggered by a                 Accordingly, in this work F1 and BA are both used to assess
Bernoulli-sampled packet loss with probabilityρ.                               NIDS performance related to the AC task.

3.5. Few-shot scenarios methodology                                               Furthermore,weutilizetheReceiverOperatingCharacteris-
  In this work, we explore scenarios characterized by limited                  tic (ROC) curve and the Area Under the ROC Curve (AUC) to
data availability for 0-day attacks, evaluating the impact of the              evaluatethedetectioncapabilitiesofanincrementalclassifier.
numberofsamplesavailableforincrementaltrainingonclassi-                        The ROC curve visually represents the performance of binary
fication and detection performance.                                            classification(viz.detection)models,illustratinghowtheirper-
  This scenario is commonly known as FSCIL, as it inter-                       formance changes with adjustments to detection thresholds. In
sects with both CIL and Few-Shot Learning (FSL). FSCIL in-                     thisstudy,weusethesumofsoftoutputsassociatedwithattack
volves enhancing a base classifier to accommodate the knowl-                   classes as the detection score.  Instead, the AUC is a numeric
edge of new classes (Cnew) using a notably restricted number                   measuresummarizingtheoverallperformanceofabinaryclas-
of samples.  Accordingly, the updated model is trained using                   sification model by quantifying the area under the ROC curve.
D =Dmem∪Dfew as the training dataset, whereDfew≪Dnew                           A perfect (or random) model has an AUC of 100% (or 50%).
(viz.|Dfew|=K·|Cnew|). The number of samples for each new                      HigherAUCvaluesindicatebetterdiscriminationbetweenpos-
class K is also referred to as “shots” in FSCIL literature.  To                itive and negative cases. Additionally, we consider the Partial
recreate a few-shot scenario, we perform an incremental train-                 Area Under the ROC Curve (PAUC), focusing on the interval
ingprocedureacrossmultipleepisodes,whereeachepisodere-                         enclosedbyamaximumFalsePositiveRate(FPR)valueof1%
lies on a different set of K shots.  These shots are randomly                  to evaluate model performance over a restricted range of FPRs
sampled(withoutreplacement)fromDnew togenerateadistinct                        in the ROC curve.
Dfew for each episode. The latter set is used to learn the new                    Specifically, in this work we resort on the macro version
apps (Cnew) in a FSCIL context.  As a result, multiple evalua-                 of AUC and PAUC. This allows us (i) computing the (P)AUC
tion phases (corresponding to the number of episodes) are car-                 givenanarbitrarysetofattackclassesw.r.t.thebenignone,and
ried out on the same testing data for each incremental model in                (ii) avoiding the class-imbalance effect on such metrics.  Ac-
thiscontext. Also,inwhatfollows,weassesstheimpactacross                        cordingly, given an arbitrary set of malicious traffic classes—
various shot values, notably K ={5,25,50,100,200}.                             denoted asCm—and the benign class   cb, the macro-(P)AUC is
                                                                            7
```


### PDF page 8

[View original page, figures and tables](assets/page-008.png)

```text
Table 4: Categorization of attack classes within leveraged datasets, indicating the nature of devices used, including real (/tv) or emulated (♂robot) devices.

        Dataset                      Period                                           Attack Category                                                    Devices
                                       (D)DoS                                 Info Gathering                    MITM                    Injection                Malware
        IoT-23 [8]         2018–19     DDoS                      C&C-Heartbeat            N.A.              C&C               Attack                       /tv
                                       Okiru                     Port Scanning
                                       DoS SYN Flood             Host Discovery
        IoT-NID [10]              2019 Mirai ACK Flood           OS/Version Scanning      ARP Spoofing      N.A.                       Mirai Telnet Bruteforce/tv
                                       Mirai HTTP Flood          Port Scanning
                                       Mirai UDP Flood
                                       DDoS                                                                 Injection         Backdoor                     /tv
        TON-IoT [9]        2019-20     DoS                       Scanning                 MITM              XSS               Password                     ♂robot
                                                                                                                              Ransomware
                                       DDoS HTTP Flood           OS Fingerprinting                          SQL Injection     Backdoor
        Edge-IIoT [11]      2021–22    DDoS ICMP Flood           Port Scanning            MITM              Uploading         Password                     /tv
                                       DDoS TCP SYN Flood        Vulnerability Scanner                      XSS               Ransomware                   ♂robot
                                       DDoS UDP Flood

















                                        (a)IoT-23 [8]                                                           (b)IoT-NID [10]















                                        (c)TON-IoT [9]                                                        (d)Edge-IIoT [11]

          Figure 2: Biflows distribution of leveraged IoT datasets. Various hatch patterns are employed to distinguish between different attack categories.


defined as:                                                                            new classes (attacks), respectively. Lower values of these met-
                                                X                                      rics indicate better performance.
        macro-(P)AUC(θ,Cm)=   1|Cm|                   (P)AUC(ci,cb)     (6)
                                               ci∈Cm                                   4.2. Datasets, Traffic Segmentation, and Input Selection

Hereinafter, for brevity, we refer to the macro-(P)AUC simply                          Taxonomy of IoT Traffic Datasets.  In this study, we inves-
as (P)AUC. In what follows, AUC and PAUC are are used to                               tigated 4 datasets comprising network traffic originating from
assess NIDS performance associated with the bMD task.                                  IoT devices, collected from 2019 onwards [45].  They differ
   To gain deeper insights into the classification/detection per-                      in the nature of the malicious traffic they comprise.  In detail,
formance gap between an incremental model and its counter-                             IoT-23 and IoT-NID encompass traffic generated by real de-
parttrained-from-scratch,weintroduceadifferentialversionof                             vices, while TON-IoT and Edge-IIoT consist of traffic gen-
eachevaluationmetric. ForanyarbitrarymetricX,itsdifferen-                              erated by both real and emulated devices.  Furthermore, they
tial version, denoted asX Drop, is computed as follows:                                incorporate a broad spectrum of attacks, where specific types

              XDrop(C)=X(θScratch;C)−X(θCIL;C)             (7)                         are evident across multiple datasets, while others remain ex-
                                                                                       clusive to particular datasets (see Tab. 4 for a detailed taxon-
This kind of metric is further broken down by sets of classes                          omy).It is important to note that this classification of attack
into XDropAll for Call, XDropOld for Cold, and XDropNew                                classes is further corroborated by prominent surveys in this
for Cnew, representing the drops associated with all, old, and                         domain [45, 46, 47].Specifically, all datasets include       UDP
                                                                                    8
```


### PDF page 9

[View original page, figures and tables](assets/page-009.png)

```text
and SYN flooding attacks, with TCP flooding attacks exclu-                     efit of using additional inputs such as Time-To-Live (TTL) and
sively present in IoT-23 and TON-IoT.   Furthermore, only                      TCPFlags(FLG).Indetail,PLrepresentsthesizeofthepacket,
IoT-NID includes ACK flooding attacks and Edge-IIoT ex-                        IAT indicates the time gap between two consecutive packets,
hibits ICMP flooding attacks, while both present HTTP flood-                   WIN denotes the TCP window size (with a value set to 0 for
ing attacks.   These attacks aim to disrupt service availabil-                 UDP packets), DIR signifies the direction of the packet (+1 for
ity by inundating it with excessive traffic from one or multi-                 upstream, −1 for downstream), TTL is the maximum number
ple sources.  The datasets cover various scanning attacks, in-                 of hop that a packet can traverse through a network before it
cluding port scanning (in IoT-23, IoT-NID, TON-IoT, and                        is discarded, and FLG refer to control bits in the TCP header.
Edge-IIoT), OS scanning (in IoT-NID and Edge-IIoT), vul-                       We underline that certain fields like transport ports and IP ad-
nerability scanning attacks (inEdge-IIoT), and host scanning                   dresses are intentionally omitted from our model’s training to
(in IoT-NID).Although these classes do not refer to actual at-                 avoid undue bias [49].
tacks, they usually represent the reconnaissance phase that is                    Accordingly,inthiswork,weconsidertheper-packetproper-
preparatory for the exploitation of network attacks.   Specifi-                tiesofthefirstNp packetstodesignanNIDSabletodetectIoT-
cally, these (malicious) actions play a crucial role in identify-              focused threats in an early fashion, i.e. achieving robust attack
ing vulnerabilities and streamlining unauthorized access.Ad-                   detectionandclassificationperformancewithoutcompromising
ditionally, IoT-23 incorporates keep-alive attacks (viz. C&C-                  theearlinessofitsoutcomes. Consequently,weextracttimese-
heartbeat) to exploit vulnerabilities.   Man-in-the-middle at-                 riesdataforeachbiflow,encompassingasequencelengthofNp
tacks are observed, encompassing ARP spoofing in IoT-NID,                      packetsforthespecifiedper-packetproperties. Ifthetimeseries
TON-IoT, and Edge-IIoT.  TON-IoT incorporates also ICMP                        data consists of less than Np packets, we employ zero-padding
and DHCP spoofing, while Edge-IIoT involves DNS spoof-                         to reach the necessary length.  Previous studies [49, 50] have
ing. Theseattacksconsistofunauthorizedinterceptionofcom-                       established that the initial Np = 10 packets of each biflow are
munications between two parties.  SQL injection and XSS are                    sufficient for accomplishing the aforementioned goal:  hence,
collected in TON-IoT and Edge-IIoT, and HTTP injection in                      weputforwardthisdesignchoiceinthefollowingexperiments,
Edge-IIoT, involving the unauthorized entry of code compro-                    while also providing a sensitivity analysis w.r.t. Np.
mising system integrity.  Furthermore, IoT-23 includes Com-
mand and Control (C&C) attacks, involving unauthorized in-                     4.3. DL Model Architecture
filtration to gain control over compromised systems for mali-                     In this work, we leverage a 2D-CNN architecture, consisting
cious activities. Other included attacks involve brute-force at-               oftwoconvolutionallayers(Conv2D),followedbypoolingand
tempts on HTTP (IoT-23, TON-IoT, and Edge-IIoT), telnet                        normalization operations, and a Dense layer responsible for
(IoT-NID and IoT-23), FTP (TON-IoT), and SSH (IoT-23).                         generatingthemodel’soutput. ItisnoteworthythatCNN-based
These attacks systematically test various password combina-                    modelsfindextensiveapplicationinSOTAapproachesfortraf-
tions to gain unauthorized access.   Finally, backdoor (unau-                  fic fingerprinting [51, 52]. The entire architecture involves ap-
thorized access points for remote entry) and ransomware (ma-                   proximately 540k trainable parameters.
licious software encrypting files) are present in TON-IoT and                     The network is fed with 10×4 [packets× fields] per biflow
Edge-IIoT.                                                                     astheinput x. Aswehavechosentoemployfine-tuningfamily
  Concerning  the  devices  utilized  for  dataset  collection,                approaches, the backbone remains unchanged throughout each
IoT-23 and IoT-NID datasets employ real devices, encom-                        incremental iteration, while the head (i.e. the final layer of the
passing both smart home and general-purpose devices. In con-                   network) is expanded to accommodate as many neurons as the
trast,Edge-IIoTandTON-IoTdatasetsleverageacombination                          new classes introduced in that specific episode.  Incremental
of emulated and real devices, including sensors and general-                   training begins with the parameter values derived after the pre-
purpose devices.                                                               ceding training stage (θ∗).
Traffic Object Definition. A commonly utilized traffic object                     Itisworthnotingthattheproposedmethodologyisdesigned
for early detection is the biflow [48].  The latter is a bidirec-              to be architecture-agnostic—i.e., while it has been applied to a
tional flow, encompassing packets that share an identical quin-                specificDLarchitecture,itcanbeadaptedforuseacrossvarious
tuple (source IP, source port, destination IP, destination port,               other DL architectures. This flexibility enhances its applicabil-
and transport protocol), with the option of interchanging the                  ity in diverse settings.
source and destination.   Based on the aforementioned traffic
segmentation, the dataset compositions in terms of number of                   4.4. Class Incremental Learning Scenario
biflowsforeachclassareillustratedinFigs. 2a–2d. Inthisvisu-                       In this work, our main emphasis is on adapting NIDS to new
alization,thebenignclassisdepictedingreen,whiletheattack                       emerging attacks targeting IoT devices.   Specifically, we as-
classesaredifferentiatedbyvariouscolors,eachcorresponding                      sumetheavailabilityofabaseNIDSmodelabletodiscriminate
to a specific dataset.                                                         between legitimate traffic and a number of known attacks. The
DefinitionofTrafficInput. Inthisstudy,weconsiderfourper-                       objective is then to include into the model new attack classes
packet properties, specifically the network-layer packet length                upon their discovery in an incremental fashion.In our experi-
(PL),inter-arrivaltime(IAT),TCPwindowsize(WIN),anddi-                          mental investigations, we delve into a prevalent cyber-security
rection(DIR).Furthermore,wealsoexaminethepotentialben-                         scenario involving 0-day attacks.   We focus on the scenario
                                                                            9
```


### PDF page 10

[View original page, figures and tables](assets/page-010.png)

```text
(a)IoT-23                                (b)TON-IoT                              (c)IoT-NID                            (d)Edge-IIoT

Figure 3: ROC curves averaged across increments for CIL approaches, Scratch, and base model. Curves are depicted with a linear scale from 0 to 10−2 and then
with a logarithmic scale.Annotations report the TPR of       Cold (Cnew) for the base model obtained with FPR= 10−2, showcasing its capability to detect known—viz.
misuse detection—and 0-day attacks—viz. anomaly detection—, respectively.

Table 5:Detection performance in terms of PAUC Drop (lower values are the better) of CIL approaches and    Base Model. Performance expressed as average and
std. dev. across the runs.Furthermore, we present the PAUC values derived from training the model from scratch. Specifically, the obtained PAUC is      ≈83% for
IoT-23,≈94%forTON-IoT,≈91%forIoT-NID,and≈99%forEdge-IIoT. Thebest(resp. worst)CILapproachisreportedwithgreen(resp. red)coloredcell;
the bestapproach overall is reported inbold.


                  Approach                      IoT-23                             TON-IoT                             IoT-NID                           Edge-IIoT
                                      All         Old       New        All         Old        New        All         Old        New         All         Old        New

                  FT                31.55     31.72     30.71     37.55     39.00     25.94     39.83     39.89      39.30     47.39     47.42     47.09
                  FT-Mem               31.36     31.20  32.18     22.27      22.92      17.04     30.08      30.95      23.10      24.43      25.34      12.61
                  LwF               25.83     25.23     28.81     14.69     14.30     17.82     24.87     23.79      33.54     28.60     29.15     21.41
                  iCaRL+              29.65     31.24     21.69     34.22      35.24  26.12     31.17      32.00      24.51      35.04      35.18      33.16
                  LUCIR             28.91     28.19     32.51     12.07     10.96     20.89     25.89     24.89      33.92     11.22     11.36       9.43
                  EEIL                  28.62     30.09 21.24     22.11      23.10      14.18     29.12      30.86   15.19      25.51      26.97     6.47
                  EWC               28.92     29.01     28.45     16.78     16.62     18.05     32.47     33.52      24.06     21.37     21.85     15.13
                  BiC               18.77     17.54     24.94      4.20       3.95      6.22    18.18     16.74      29.70      8.93      8.70      11.94
                  Base  Model        3.80       0.71     19.25       0.71     −0.04       6.68       2.02     −1.11     27.01     −0.05     −0.57       6.70


where a new attack is added to the model.  This approach is                              of 10−4.  For memory-based CIL approaches, we set a mem-
based on the reasonable assumption that multiple new attacks                             ory composed of 25 exemplars per class—viz. memory size is
do not emerge simultaneously.  Therefore, when samples of a                              obtained as 25×|C|.As for input perturbation, while  flipping
novel attack are detected (and labeled as such), they are incre-                         and slicing are static, jittering and timeout are parametrized.
mentally incorporated into the NIDS.                                                     Notably, for jittering, we empirically set parameters (µ =  0,
   To match the aforementioned assumptions, for each consid-                             σ =  0.3).  Differently from Cerasuolo et al. [44], which in-
ered dataset (consisting of N attack classes plus the benign                             troducedthistransformationtoaugmenttrafficbiflowspreserv-
class), our evaluation consists of N runs.  Specifically, nth run                        ing the biflow semantics (with µ = 0, σ = 0.03), we choose
is obtained by excluding nth attack from the base model train-                           σ = 0.3 to alter appreciably the temporal dynamics of biflows
ing, and treating it as a 0-day.  Hence, in each run a different                         by introducing a delay in the reception of packets of ±8ms
attack is treated as new and added incrementally.  Since this                            (viz.  σ =  4ms).  For the timeout perturbation, we have se-
approach entails conducting N (incremental) experiments for a                            lected a packet loss rate of ρ =  10%.Concerning the com-
given dataset, the results are presented as the average and stan-                        putationalresourcesutilizedfortheexperimentalcampaign,all
dard deviation of the metrics discussed in Sec. 4.1 across all                           analyseswereperformedonamachineequippedwith2Intel(R)
the runs.  Notably, for the FSCIL scenario (Sec. 3.5), results                           Xeon(R) Gold 6252N CPUs running at 2.30 GHz and boasting
areexpressedasaverageandstandarddeviationacrossdifferent                                 378 GB of memory.
episodes(i.e.10inoursetup)andacrosstheN runs. Evaluation
of each model follows the hold-out method, utilizing 70% and                             5. Experimental Results
30% of the dataset as the training and test sets, respectively.                             Inthissection,weaddressthebMDtaskinSec.5.1andthen
   The experiments being reported rely on the FACIL frame-                               the incremental AC task in Sec. 5.2. Notably, we benchmarked
work [33], employing the following training parameters:  200                             several CIL approaches, namely FT, FT-Mem, LwF, iCaRL+,
epochs with a patience of 20, an initial learning rate of 0.1, a                         LUCIR, EEIL, EWC, and BiC, against the 4 IoT attack datasets
learning rate decay factor of 3, and a minimum learning rate                             considered:   IoT-23,  TON-IoT,  IoT-NID,  and Edge-IIoT.
                                                                                    10
```


### PDF page 11

[View original page, figures and tables](assets/page-011.png)

```text
Table 6:CIL approaches performance—in terms of F1 and BA Drop (lower values are the better)—and training time.Performance and time are expressed as
average and std. dev. on the runs. Time saved is computed as percentage w.r.t. training time required by Scratch. Additionally, we specify the F1 (resp. BA)
achieved by training the models from scratch. In particular, IoT-23 attains≈89% (resp. ≈90%), TON-IoT≈98% (resp. ≈99%), IoT-NID≈97% (resp. ≈96%),
andEdge-IIoT≈79% (resp.≈80%). Thebest (resp. worst) CIL approach is reported with green (resp. red) colored cell.


                Dataset     Approach                             F1 Drop [%]                                                      BA Drop [%]                                   TimeSaved [%]
                                                  All                   Old                  New                  All                   Old                   New
                             FT              81.30±  3.90      85.45±  4.33     60.51±11.06       75.13±  7.37     88.73±  3.09        20.77±47.43           87
                             FT-Mem           35.92±14.26     36.46±14.85     33.22±13.86     35.97±19.69     40.21±14.76        19.01±45.17            85
                             LwF             39.53±13.01       30.24±14.08      85.96±  9.73      34.19±12.05      26.50±16.49         64.94±29.36           81
                             iCaRL+         29.96±24.98     30.01±28.35     29.75±11.21     29.23±27.51     33.70±25.77        11.36±38.82                   79
                             LUCIR           42.02±20.22       43.86±22.94      32.83±13.65       40.54±14.81      47.79±23.51         11.54±38.50           78
                             EEIL              28.99±16.08     27.91±18.13     34.41±11.24     30.03±20.85     34.63±17.50        11.65±38.95                94
                             EWC             20.62±  6.94      19.83±  7.53     24.55±  6.31      21.11±12.06      25.04±11.57          5.38±26.24           80
                             BiC             10.92±  4.30       9.08±  4.64     20.13±  4.68       9.67±  7.08     10.70±  8.44          5.56±19.30            80
                             FT              91.12±  3.74      92.72±  4.02     78.35±12.52       85.62±  6.70     94.87±  3.18        20.89±41.92           93
                             FT-Mem           19.28±  6.46     16.68±  7.18     40.09±17.23     17.48±  7.80     19.34±  8.77          4.44±15.27            93
                             LwF             33.81±15.02       25.79±16.91      97.95±  2.10      29.07±16.84      21.56±17.94         81.63±33.14           91
                             iCaRL+         27.58±23.77     25.18±25.96     46.78±18.09     23.81±22.49     26.47±26.02          5.21±12.60            90
                             LUCIR           13.75±  6.95      12.21±  7.18     26.04±23.02       12.61±  7.61     14.28±  8.55         0.92±  3.73          89
                             EEIL              21.10±  7.85     18.85±  7.37     39.10±17.38     20.03±  6.39     22.43±  8.03          3.29±  8.60          97
                             EWC             12.75±  5.22      10.20±  4.61     33.14±18.18       10.16±  3.59     11.56±  4.01         0.33±  3.87          90
                             BiC               5.48±  4.92      3.57±  3.81     20.82±19.82        5.03±  4.72       4.09±  4.02        11.58±24.20            90

                             FT              90.17±  4.53      91.43±  4.91     80.08±24.35       77.13±  5.72     88.68±  6.66      − 3.70±  4.37           96
                             FT-Mem           28.84±25.38     25.96±27.64     51.87±27.66     20.25±23.71      23.64±26.9     − 3.51±  4.28             96
                             LwF             47.12±26.75       40.85±29.91      97.22±  2.40      36.63±23.67      28.11±26.86         96.29±  4.36          94
                             iCaRL+         37.08±31.65     35.28±35.17     51.48±25.87     26.61±31.18     30.90±35.42    − 3.41±  4.26                     92
                             LUCIR           32.40±19.51       29.57±21.50      55.01±27.91       25.16±16.89      28.90±19.74       − 1.08±  4.31           93
                             EEIL              23.25±11.79     20.30±14.28     46.81±19.26     14.99±11.64     17.61±13.20    − 3.41±  4.26                  97
                             EWC             26.01±13.93       23.70±16.25      44.45±27.93       18.45±13.54      21.56±15.26       − 3.31±  4.23           93
                             BiC             18.16±13.50       15.74±12.40      37.47±32.45       11.56±10.06      11.73±12.52        10.39±28.47            93
                             FT              73.67±  7.46      74.34±  7.97     64.91±36.68       67.88±  8.39     73.97±  9.21      − 5.18±55.81            98
                             FT-Mem           36.71±15.53     36.80±15.91     35.50±38.98     25.11±16.41     28.64±18.32            −17.27±36.99             97
                             LwF             62.22±  9.00      60.91±10.18      79.29±33.50       54.27±15.22      52.66±15.91         73.51±40.74           98
                             iCaRL+         60.69±23.68     61.07±23.40     55.76±44.70     54.41±26.57     59.35±27.27    − 4.89±55.73                      96
                             LUCIR           23.21±15.63       23.00±15.83      25.94±37.87       15.85±14.05      17.67±14.71       − 6.03±53.31            96
                             EEIL              34.21±15.29     33.20±14.88     47.35±43.15     24.29±14.52     26.85±14.46    − 6.34±53.42             97
                             EWC             23.25±15.79       23.26±16.81      23.14±31.47       14.79±16.62      17.11±18.56       −13.06±44.85            96
                             BiC             12.85±  7.88      11.82±  7.47     26.14±24.42        9.76±  7.15       9.90±  8.31          8.16±38.39         96


Subsequently, we explore the hyperparameters crucial for in-                                  forming approach in differentiating between benign and ma-
cremental training—i.e.   number of memory biflows—and for                                    licious classes, resulting in a PAUC Drop All of ≈ 32% for
traffic input definition—i.e.   number of packets and set of fea-                             IoT-23,≈38% for TON-IoT,≈40% for IoT-NID, and≈48%
ture used—in Sec. 5.3.  Finally, in Sec. 5.4, we determine the                                forEdge-IIoT. Duetopronouncedforgetting,theperformance
optimal configuration for each dataset and discuss the results.                               on Cold  consistently deteriorates,  obtaining values of PAUC
                                                                                              Drop≥32%. Moreover, the same model encounters difficulty
5.1. Misuse Detection                                                                         in distinguishing betweenCnew and the benign class, achieving
Aim of the analysis:  In this section, we investigate the per-                                drop values higher than ≈ 26%.  These results underscore the
formanceofincrementalNIDS,obtainedwithdifferentCILap-                                         necessity of implementing strategies to mitigate forgetting.

proaches, in distinguishing between legitimate and malicious                                     The adoption of memory is of clear benefit for bMD perfor-
traffic (viz. bMD task).                                                                      mance. Indeed,evenFT-MemattainsaPAUCDropAllof≈22%
The results are depicted using the ROC curves in Fig. 3 and                                   for TON-IoT,≈30% for IoT-NID, and≈24% for Edge-IIoT.
quantified through PAUC Drop in Tab. 5.  It is worth noting                                   Moreover,itsubstantiallyenhancesperformanceacrosstheOld
thatROCcurvesareaveragedacrossallincrements,asdetailed                                        classes, achieving ≈ 23% for TON-IoT, ≈ 31% for IoT-NID,
in Sec. 4.1.  Additionally, we recall that the detection score is                             and≈25% for Edge-IIoT of PAUC Drop. Even withinCnew,
computed as the sum of the soft outputs associated with attack                                notable improvements are evident, with drop of ≈ 17% for
classes.                                                                                      TON-IoT,≈23%forIoT-NID,and≈13%forEdge-IIoT. Dif-
   Across all examined datasets, the FT method, which is the                                  ferently, for IoT-23 the performance of FT-Mem is not too far
most straightforward approach, turns out to be the worst per-                                 fromFT,reachingsimilarvaluesforCallandCold andworsening
                                                                                         11
```


### PDF page 12

[View original page, figures and tables](assets/page-012.png)

```text
the drop value onCnew. This underlines the need for distilling                  By  implementing  various  mitigation  strategies,  the  drop
the behavior of the base model other than simply replaying old               across different subsets of attacks tends to diminish.  Specif-
class samples.                                                               ically, FT-Mem (viz. FT plus rehearsal techniques) notably en-
  Furthermore, the sole addition of a regularization term (i.e.              hances FT’s performance, resulting in a decrease of≈36% on
LwF)failstoyieldimprovementforEdge-IIoTbutobtainsbet-                        IoT-23,≈19%onTON-IoT,≈29%onIoT-NID,and≈37%on
ter performance on the other datasets, reducing the drop for all             Edge-IIoT. Solely relying on regularization techniques, such
classes to≈25% for IoT-23,≈15% for TON-IoT, and≈25%                          asLwF,hampersthemodel’sabilitytoincludenewclassknowl-
forIoT-NID.                                                                  edge, leading to a drop≥ 79%. However, leveraging multiple
  Combining mitigation strategies leads to improved perfor-                  strategies yields improved outcomes. For instance, the combi-
mance for TON-IoT and Edge-IIoT. In detail, LUCIR outper-                    nationofstrategiesbenefitsIoT-23,whereEWCexhibitsadrop
formspreviouslymentionedapproachesreachingaPAUCDrop                          of≈ 21% onCall, ≈ 20% onCold, and≈ 25% onCnew.  Simi-
All of≈12% and≈11%, respectively.                                            larly,inthecaseofTON-IoT,EWCdemonstratesdropsof≈13%,
  BiCemergesasthemosteffectiveCILapproach,demonstrat-                        ≈10%, and≈33% on all, old, and newclasssubsets, respec-
ing better detection performance w.r.t. other approaches.  For               tively. Among the methods explored, EEIL exhibits the lowest
instance, it achieves the lowest drop value on TON-IoT, reach-               drops for all and oldclasssubsets on             IoT-NID (≈ 23% and
ing a≈4% PAUC Drop All and Old, and≈6% of PAUC Drop                          ≈ 20%, respectively), while EWC achieves the most favorable
New.                                                                         drop for new classes (≈44%). Finally, concerningEdge-IIoT,
  Counter-intuitively, the base model achieves the most ro-                  LUCIR obtains the lowest drops for all and oldclasssubsets
bust detection performance.  Specifically, for all the datasets,             (≈ 23% for both), whereas EWC achieves the most promising
it achieves better detection performance than Scratch forCall                result for new classes (≈23%).
andCold presenting low PAUC Drop values, in some cases also                     Finally,BiCemergedasthetopperformeracrossalldatasets,
<0. As forCnew, it presents PAUC Drop values>0 that results                  showcasing  the  most  favorable  outcomes  in  terms  of  F1
the best across all the considered approaches only for IoT-23                DropAll.  Notably, it achieved ≈ 11% on IoT-23, ≈ 5% on
with a ≈ 19% PAUC Drop New.  Conversely, for TON-IoT, it                     TON-IoT, ≈ 18% on IoT-NID, and ≈ 13% on Edge-IIoT.
exhibits a drop of≈7% for the new class and it is surpassed by               Furthermore, BiC obtains the lowest F1 DropOld values, at
BiC, obtaining a 1% lower drop (≈6%). Instead, for IoT-NID                   most below 4% on TON-IoT.  However, it exhibited relatively
and Edge-IIoT, EEIL reaches the lowest PAUC Drop New                         higher F1 DropNew, ranging from 20% to 38%.  Despite this,
with≈15%and≈6%,respectively,overperformingbasemodel                          BiC maintained the lowest F1 DropNew for all datasets ex-
which obtains≈27% and≈7%. These performance outcomes                         cept Edge-IIoT, where EWC showcased slightly superior per-
may stem from the absence of catastrophic forgetting in the                  formance regardingCnew.
base model, hence it continues detecting old classes with satis-                Inaddition,alltheconsideredapproachesprovidesubstantial
factory results while sufficiently distinguishing the new attack             timesavings(inthetrainingphase)incomparisontoScratch.
class from benign ones.                                                      Notably,theEEILapproachstandsoutwiththemostsignificant
Take-home:  BiC emerges as the most effective CIL ap-                        timesavings(exceptforEdge-IIoT)attributedtothelossfunc-
proach to address the bMD task.  However, utilizing a (sim-                  tion leading the incremental training process and to the early
ple) base classifier may suffice for distinguishing between                  stopping procedure. The remaining approaches exhibit slightly
malicious and benign traffic (in contrast to the set of CIL                  lowertimesavings,influencedbyboththelossfunctionandthe
techniquesconsidered). ThisisparticularlynotableinIoT-23                     utilization of memory samples. Specifically,iCaRL+ offers the
while for the other three datasets, incremental approaches (viz.             least time savings on IoT-23 (≈79%) and IoT-NID (≈92%).
BiC orEEIL) lead to (slightly) better detection performance on               On TON-IoT, LUCIR turns out to be the most time-consuming
the new class. This finding highlights thatcutting-edge incre-               approach (≈ 89%), whereas for Edge-IIoT, iCaRL+, LUCIR,
mental techniques beyond the current state-of-the-art are                    EWC, and BiC require the same training time (96% saving w.r.t.
needed to improve detection performance.                                     Scratch). The remaining approaches offer time savings inter-
                                                                             mediate betweenFTand the most time-consuming approaches.
5.2. Attack Classification                                                   Take-home:  Looking at Tab. 6,   memory-free approaches
Aim of the analysis:  In this section, we evaluate the perfor-               (i.e. FT  and LwF)  struggle  to  obtain  satisfactory  perfor-
mance of the attack classification task, specifically focusing on            mance, while using a memory is more effective at handling
the ability to distinguish between malicious (viz. attack) traf-             the CIL scenario. Furthermore, the overall best-performing
ficclasses. Thisincludesassessingtheclassifier’seffectiveness                model is BiC offering performance closest to Scratch (viz.
whenanewpreviouslyunseen(i.e.,0-day)attackisintroduced                       upperbound) for all the considered datasets. Finally, adopting
into the underlying NIDS base model.                                         BiCcanleadtotrainingtimesavingsofupto80%compared
AccordingtotheresultspresentedinTab.6,FTattainstheworst                      toScratchonIoT-23 (≈330s and≈1800s, resp.).
performance, showing significant drops across all class sets.
Specifically,FT incurs an F1 Drop≥74% forCall andCold and                    5.3. Investigating (Class Incremental) Hyperparameters
≥61%forCnew. Thisresultisconsistentwiththefindingsofthe                      Aim of the analysis: This section analyzes several key hyper-
bMDtask,suggestingthattheabsenceofmemorydetrimentally                        parametersessentialfortheincrementalmodeltoimproveclas-
affects performance in both tasks.                                           sification and detection performance. Specifically, we focus on
                                                                         12
```


### PDF page 13

[View original page, figures and tables](assets/page-013.png)

```text
(a) All classes                                    (b) Old classes                                  (c) New classes
















                       (d) All classes                                     (e) Old classes                                 (f) New classes

Figure 4:  Analyzing memory size impact on incremental model performance in terms of F1 (a, b, c) and PAUC Drop (d, e,  f)—viz. lower values are better.
Performance, measured by average and standard deviation across runs, is categorized into All, Old, and New classes.


(a) the number of per-class biflows stored during the rehearsal                  creasing F1 DropAll across all datasets.  Specifically, IoT-23
process, (b) the number of packets collected for each biflow,                    and Edge-IIoT exhibit continuous improvement with increas-
and (c) the input set extracted from biflows and used for the                    ing memory, reaching ≈ 13% and ≈ 5% with #mem=200, re-
incremental model.                                                               spectively.  On the other hand, the performance of IoT-NID
Through  this  analysis,  our  goal  is  to  determine  an  opti-                improves up to #mem=100, reaching≈4% F1 DropAll, then it
mal  configuration ⟨#mem,#pkts,inputs⟩,  where  #mem  indi-                      experiencesaslightdecrease. Incontrast,TON-IoTexperiences
cates  the  number  of  per-class  biflows,  #pkts  the  number                  a slight deterioration after reaching 50 biflows per class, where
of per-biflow packets, and inputs the (sub)set of per-packet                     ≈4% F1 DropAll is exhibited.
features leveraged—  base stands for [PL,  IAT,  DIR,  WIN]                         A similar pattern is shown forCall for IoT-23, Edge-IIoT,
while  expanded  for  [PL,  IAT,  DIR,  WIN,  TTL,  FLG]—                        and   IoT-NID.        Conversely,    TON-IoT   improves   until
that enhances the classification and detection performance of                    #mem=100, obtaining a≈2% F1 DropOld.
our NIDS.                                                                           However,  a  distinct  pattern  emerges  for Cnew.    Notably,
   To achieve this, we select BiC since it is the top-performer                  IoT-23 and Edge-IIoT exhibit continuous enhancement in
both in classification and in detection tasks and systematically                 F1 DropNew as memory increases, eventually achieving op-
compare various configurations against the one analyzed in the                   timal values of≈ 8% and≈ 10%, respectively.  In the case of
previous sections (i.e. ⟨25,10,base⟩) across all datasets.   In                  IoT-NID, performance improves up to 100 biflows per class,
the sensitivity analysis, rather than conducting a grid search                   reaching≈18%, before experiencing a decline when utilizing
(i.e. Cartesian product of all combinations), we employ a sub-                   #mem = 200. Similarly, TON-IoT shows improvement with 50
optimal solution by exploring a narrowed scope of solutions.                     biflows per class, resulting in a drop of≈17%, but then deteri-
This involves optimizing each parameter individually while                       orates until reaching a drop of≈48% with #mem = 200. These
maintaining the others at their base values (i.e. #mem = 25,                     phenomena may arise from an increase in old attacks biflows,
#pkts=10,andinputs=base). Bestvaluesaremainlydrivenby                            causing the model to shift its bias from new to old attacks.
the F1 in the AC task, as there is a negligible loss w.r.t. PAUC-                   As for detection performance,Call andCold exhibit the same
optimal configuration.                                                           pattern.   Notably, IoT-23 and Edge-IIoT have a decreas-
Memory Size. Herein, we examine the performance variations                       ing trend until #mem=200, reaching ≈ 8% and ≈ 4% PAUC
w.r.t.thenumberofper-classbiflowsstoredinmemoryandsub-                           DropAll, respectively.  For IoT-NID, performance has a peak
sequentlyrepresentedduringincrementaltraining(viz. #mem).                        with 50 per-class biflows, obtaining≈9% PAUC DropAll, then
This analysis is depicted in Fig. 4 for AC and bMD tasks, both                   a decrease,  and the best value is obtained with #mem=200
broken down by class sets—All, Old, and New.                                     (≈ 6% PAUC DropAll).  Then, TON-IoT continues improving
   As the memory size increases, there is a general trend of de-                 until 100 per-class biflows with≈2% drop onCall and no drop
                                                                             13
```


### PDF page 14

[View original page, figures and tables](assets/page-014.png)

```text
(a) All classes                                  (b) Old classes                             (c) New classes
















                           (d) All classes                                  (e) Old classes                             (f) New classes

Figure 5: Analysis of performance in terms of F1 (a, b, c) and PAUC (d, e, f) by varying the number of packets considered per each biflow—viz. higher values are
better. Performance is expressed as the average and standard deviation across multiple runs and is broken down into All, Old, and New classes.


onCold then performance remains stable with #mem=200.                           highest F1 is reached with 8 packets, namely ≈ 67% for Call
  ConcerningCnew, for Edge-IIoT with only 50 biflows per-                       andCold, and≈ 60% forCnew.  As for IoT-NID, leveraging 5
class we obtain a ≈ 11% PAUC Drop that remains stable for                       packets, we achieved≈85%,≈88%, and≈67% F1 on all, old,
higher #mem values.    For IoT-23,  we obtain the best de-                      and new classes, respectively. For new classes, the best perfor-
tection performance with 200 per-class biflows, exhibiting a                    mance(≈71%)wasobtainedwith6packets. Lastly,leveraging
≈ 13% drop.  For IoT-NID, the best performance is reached                       9 packets forTON-IoT, we achieved≈93%,≈95%, and≈82%
with 200 with≈6% drop. Conversely, for TON-IoT detection                        F1 onCall,Cold, andCnew, respectively.
performance remains quite stable, reaching the best value with                     As for detection performance, we reach highest PAUC (≈
#mem=100 (≈5% PAUC DropNew).                                                    66% on Call) for IoT-23 with #pkts=7.  For Edge-IIoT and
Take-home:   From  these  findings,  we  selected  #mem=200                     IoT-NID, we obtain best detection performance with #pkts=6,
for Edge-IIoT and IoT-23,  #mem=100 for IoT-NID,  and                           reaching a≈92% and≈77% PAUC All, respectively.  Lastly,
#mem=50 for TON-IoT, based on the best F1. It is worth not-                     for TON-IoT best detection performance is reached with 10
ing that, while Edge-IIoT and IoT-23 show the best F1 and                       packets with a≈90% PAUC for all classes.
PAUC with the same memory size, the best F1 for TON-IoT                            Although for Call and Cold the standard deviations are con-
and IoT-NID results in only a 1% and 6% loss of PAUC, re-                       tained, they are notably higher forCnew. This variance may be
spectively.                                                                     attributedtothedifferentimpactsofspecificnewattackclasses
Number of Packets. Next, we examine how the performance                         when incrementally integrated into the model. Such effects are
of the incremental model is affected by varying the number of                   consistent across all utilized packet numbers and are promi-
packets considered for each biflow.  In our previous analysis,                  nently illustrated in Figs. 5c and 5f.  This pattern highlights
we fixed the number of packets for each biflow at 10, based on                  the non-trivial nature of the observed effects, underscoring the
the previous results of the TC field.  Differently, here we con-                complexities involved in model adaptation to new classes. Fi-
duct a sensitivity analysis on the latter parameter (i.e. #pkts) to             nally,  on the one hand,  the non-monotonic behavior of the
determine whether we can enhance the incremental classifier’s                   PAUC indicates that varying the number of packets does not
earlinesswithoutcompromising(andpossiblyevenimproving)                          affect the binary detection between benign and specific attack
overall performance. The results of this analysis are shown in                  classes.  On the other hand, tuning the number of packets pa-
Fig. 5 for AC and bMD tasks, broken down by sets of classes,                    rameterenablesanimprovedseparationamongattackclasses—
namely All, Old, and New.                                                       thus improving the F1 for Edge-IIoT andIoT-23. Therefore,
  Specifically, the best classification performance on IoT-23                   we select as the best configuration the one obtaining the higher
is reached for Call, Cold, and Cnew with 7 packets, obtaining                   F1 (in average).
≈81%,≈83%, and≈75%, respectively. For Edge-IIoT, the                            Take-home:  Based on these outcomes, we selected #pkts=7
                                                                            14
```


### PDF page 15

[View original page, figures and tables](assets/page-015.png)

```text
(a) All Classes                                  (b) Old Classes                            (c) New Classes











                         (d) All Classes                                  (e) Old Classes                            (f) New Classes

Figure6: AnalysisoffeaturessetusedasinputoftheincrementalDLmodelintermsofF1(a,b,c)andPAUC(d,e, f)—viz. highervaluesarebetter. Performance
is expressed as the average and standard deviation across multiple runs and is broken down into All, Old, and New classes.


for IoT-23, #pkts=8 for Edge-IIoT, #pkts=5 for IoT-NID,                       Edge-IIoT and inputs=expanded for all other datasets since
and#pkts=9forTON-IoT. Itshouldbenotedthat,althoughthe                         we found consistent results between F1 and PAUC.
bestPAUCandF1valuesforIoT-23areachievedwith7pack-
ets, this alignment is not mirrored in the other datasets. Specif-            5.4. Wrap-up Discussion
ically, for IoT-NID and Edge-IIoT, the highest PAUC values                       In this section, we evaluate the performance enhancements
are attained with #pkts=6, while for TON-IoT, with #pkts=10,                  attained through the selection of the best parameter configura-
whichresultsinadropofF1of2%,3%,and1%,respectively.                            tion for memory size (#mem), packet number (#pkts), and fea-
Expanded Set of Inputs.  Last, we investigate the impact of                   tureset(features). Theoutcomesofthisevaluationaredetailed
leveraging an expanded set of input (i.e. [PL,  IAT,  DIR,                    in Tab. 7. Specifically,IoT-23 demonstrates improved perfor-
WIN,  TTL,  FLG] w.r.t. the base set (i.e. [PL,  IAT,  DIR,                   mance with 7 packets per biflow, an expanded feature set, and
WIN]). For this analysis, we use the same set of inputs for the               200 samples per class.  Regarding classification of attacks, F1
classifier, both in the base and incremental steps.In this sec-               reaches≈ 87% (+9% compared to the base configuration) for
tion, we explore how leveraging different sets of features im-                Call,≈88% (+8%) forCold, and≈83% (+13%) forCnew. Sim-
pactsthetasksofclassificationanddetection,respectively. Itis                  ilarly, detection performance sees an increase of≈10% forCall
important to emphasize that these two tasks may be differently                and≈9%forCold,reaching≈73%and≈74%,respectively. For
influenced by modifications in the input features.The results                 Cnew,thenewconfigurationreaches≈70%(+13%comparedto
of this analysis are shown in Fig. 6 for the AC task and bMD                  the base configuration).
tasks, broken down by sets of classes.                                           Furthermore, with 9 packets per biflow, an expanded feature
  For  classification  performance,  we  observe  an  increase                set, and 50 samples per class, TON-IoT experiences a perfor-
across all datasets, but Edge-IIoT, when using the extended                   manceenhancementof≈3%forCall andCold (achieving≈95%
set of features.  Specifically, for IoT-23 we reach≈78%, for                  and≈ 96%, respectively), and≈ 9% forCnew (≈ 86% F1).  In
IoT-NID ≈ 86%, and for TON-IoT ≈ 95% on Call.   Along-                        terms of detection, there is an improvement of approximately
sidethisenhancement,performancealsoimprovesonbothCold                         ≈7% forCall andCold, and≈1% forCnew.
and Cnew.  For instance, with the extended feature set, perfor-                  Subsequently,   with  #pkts=5,   features=expanded,   and
mance on new classes improves notably on IoT-NID, rising                      #mem=100, IoT-NID exhibits a performance enhancement of
from≈60% to≈74%. On the other hand, for Edge-IIoT, we                         ≈ 18% compared to the base configuration, achieving≈ 97%
obtain similar performance (≈66% onCall) with the extended                    acrossallattackclasses. Likewise,forOld(resp. New)classes,
setoffeaturesbutwithhighvariability(i.e.highstandarddevi-                     performanceincreasesby≈16%(resp.≈35%),reaching≈98%
ation).                                                                       (resp. ≈94%) F1. Regarding PAUC, this configuration boosts
  Intermsofdetectionperformance,significantimprovements                       detection performance by≈15% forCall,≈14% forCold, and
are observed across all datasets and subsets of classes except                ≈21% forCnew.
for Edge-IIoT where PAUC remains stable around ≈ 90%.                            Finally, Edge-IIoT demonstrates a performance increase of
Specifically, we achieve≈ 71% accuracy on IoT-23, ≈ 75%                       6%forCalland≈5%forCold,resultingina≈72%F1value,and
onIoT-NID, and≈94% onTON-IoTfor theCall subset.                               obtains≈68% forCnew (+15% w.r.t. base configuration), using
Take-home:      Therefore,    we   leverage   inputs=base   for               8 packets per biflow, the base feature set, and 200 samples per
                                                                          15
```


### PDF page 16

[View original page, figures and tables](assets/page-016.png)

```text
Table 7:  Table illustrating the performance and Average Waiting Time (AWT) of BiC in both its initial configuration and its optimal configuration selected in
previous sensitivity analyses. For each dataset, we indicate the difference in F1 Score, PAUC, and AWT of the best configuration (highlighted with gray colored
cells) over the base one: higher values are the better. AWT refers to the average time needed to wait for classifying the biflow.


    Dataset                             Config.                                              F1 Score [%]                                                      PAUC [%]                               AWT [ms]
                     #mem     #pkts        inputs               All                   Old                  New                  All                   Old                  New
                       25           10            base           78.49±4.71       80.33±6.29      69.29±  7.40      63.49±9.13       64.72±9.74       57.32±8.66          984.39
    IoT-23            200         7       expanded       87.18±1.76      88.11±1.49      82.53±12.01       73.10±8.09      73.66±9.49       70.29±9.47        977.20
                                                           +8.69             +7.78            +13.24            +9.61             +8.94            +12.97            −7.19

                       25           10            base           92.47±5.21       94.38±4.15      77.13±20.54      90.27±5.51       90.52±4.81      88.25±16.20        3884.40
    TON-IoT            50         9       expanded       95.30±1.46      96.47±1.18      85.89±  7.76      96.79±2.64      97.75±2.04      89.03±18.58        1615.40
                                                           +2.83             +3.42             +8.76             +6.52             +7.23             +0.78           −2269.00

                       25           10            base          79.06±14.32     81.47±13.11     59.74±35.92     72.60±13.52     74.04±14.58     61.08±13.81        2546.26
    IoT-NID           100         5       expanded      97.42±  1.05     97.80±  1.20    94.36±  8.60     87.10±  4.43     87.67±  4.36    82.25±12.43        2318.89
                                                           +18.36            +16.33            +34.62            +14.50            +13.63            +21.17           −227.36

                       25           10            base           66.45±8.18       67.47±7.95      53.16±35.91      89.89±9.26       90.12±8.84      86.88±19.27        3692.53
    Edge-IIoT         200         8         base         72.05±6.31      72.33±6.14      68.36±31.62       93.99±5.61      94.40±5.46      88.47±15.83        2224.44
                                                           +5.60             +4.86            +15.20            +4.10             +4.28             +1.59           −1468.08


                                                                                         6.1. Explainability
                                                                                         Aim of the analysis:   In this section,  we comprehensively
                                                                                         examine the performance of 0-day attacks (Cnew) across all
                                                                                         datasets, analyzing each attack addition to identify factors be-
                                                                                         hind the observed performance challenges. Specifically, we fo-
                                                                                         cusonCnew duetothelowF1valuesandsignificantvariability,
                                                                                         suggesting the presence of critical0-day attack addition.
                                                                                         Assuch,Fig.7illustratesthedistributionofF1fornewattacks.
                                                                                         Specifically,Edge-IIoT demonstrates the most skewed distri-
              Figure 7: F1 Score New distribution for all datasets.                      bution, with 3 specific attacks achieving < 40% F1—namely
                                                                                         Backdoor (0%), Ransomware (≈ 15%), DDoS ICMP Flood
                                                                                         (≈36%). Whileotherdatasetsdisplaymoreconcentrateddistri-
class. Moreover,detectionperformanceseesanenhancementof                                  butionsaroundtheaverage,theyalsofeatureattackswithlower
≈4% for all and old classes, with a 2% improvement observed                              F1 values—i.e.    C&C for IoT-23 (≈ 64%), OS/Version Scan-
for the new attack class.                                                                ningforIoT-NID(≈75%),andInjectionforTON-IoT(≈70%).
   In terms of Average Waiting Time (AWT), an improvement                                   To delve deeper into the analysis of these 0-day attack ad-
is experienced for all the datasets.   Notably,  TON-IoT and                             ditions, we present confusion matrices in Fig. 8.  Notably, in
Edge-IIoT exhibit the maximum improvement of≈2269 ms                                     Fig.8a,wevisualizethepredictionsfortheBackdoorattackfor
and≈1468 ms, respectively, while IoT-NID and IoT-23 save                                 BiC,demonstratingatotalconfusionwiththeUploadingattack
only≈227 ms and≈7 ms. The difference could stem from the                                 bytheincrementalmodel. However,asimilarsituationisexpe-
natureofattacksexhibitinglongerinter-arrivaltimeswithinthe                               riencedalsoinScratchpredictions(Fig.8b)withonlya≈10%
initial N packets forIoT-23 andIoT-NID. Moreover, IoT-23                                 of Backdoor biflows correctly classified.  Indeed, both attacks
notably features fewer occurrences of slow-rate attacks com-                             involveoutbounddatatransfers,typicallytoremoteservers,in-
pared to other datasets.                                                                 dicative of command and control activity, thereby sharing net-
                                                                                         work traffic patterns.
                                                                                            In the case of IoT-23 (see Figs. 8c and 8d), confusion be-
6. Real-World Challenges for Intrusion Detection Systems                                 tween the C&C and the C&C-Heartbeat attack is evident for
                                                                                         both BiC and Scratch, aligning with expectations due to their
   In this section, we delve into several real-world challenges                          shared command and control behavior, reflected in the predic-
for NIDS. These include the need for transparent decision-                               tionsoftheincrementalmodel. Thisconfusionleadstoamodel
making  processes  to  promote  widespread  adoption  of  such                           imbalance toward C&C in the incremental model (as it is the
models (Sec. 6.1), the robustness against input perturbations                            last-added attack) and toward C&C-Heartbeat in Scratch (as
and changes in network conditions (Sec. 6.2), and the capabil-                           it is the most populous between the two attack classes).
itytoeffectivelyincludenewattacksevenwithlimitedavailable                                   Regarding IoT-NID (see Figs. 8e and 8f), it is noteworthy
data(Sec.6.3). Toperformtheseanalyses,weleveragethebest                                  that some ARP Spoofing biflows are erroneously classified as
configuration obtained for each dataset (cf. Sec. 5.4).                                  OS/Version Scanning by BiC while the training-from-scratch
                                                                                    16
```


### PDF page 17

[View original page, figures and tables](assets/page-017.png)

```text
Edge-IIoT
                                                         0: Backdoor
                                                         1: DDoS HTTP Flood
                                                         2: DDoS ICMP Flood                                                                       IoT-23
                                                         3: DDoS TCP SYN Flood
                                                         4: DDoS UDP Flood                                                                     0: Attack
                                                         5: MITM                                                                               1: C&C
                                                         6: OS Fingerprinting                                                                  2: C&C-Hearbeat
                                                         7: Password                                                                           3: DDoS
                                                         8: Port Scanning                                                                      4: Okiru
                                                         9: Ransomware                                                                         5: Port Scanning
                                                        10: SQL Injection
                                                        11: Uploading
          (a)BiC                  (b)Scratch            12: Vulnerability Scanner                (c)BiC                  (d)Scratch
                                                        13: XSS


                                                               IoT-NID                                                                             TON-IoT
                                                         0: Mirai ACK Flood                                                                     0: Backdoor
                                                         1: ARP Spoofing                                                                        1: DDoS
                                                         2: Host Discovery                                                                      2: DoS
                                                         3: Mirai HTTP Flood                                                                    3: Injection
                                                         4: OS/Version Scanning                                                                 4: MITM
                                                         5: Port Scanning                                                                       5: Password
                                                         6: DoS SYN Flood                                                                       6: Ransomware
                                                         7: Mirai Telnet Bruteforce                                                             7: Scanning
                                                         8: Mirai UDP Flood                                                                     8: XSS
          (e)BiC                   (f)Scratch                                                     (g)BiC                  (h)Scratch

Figure8: Fine-grainedanalysisfocusingonthespecificadditionofthelastclassforBiCandScratch. Thelastclassunderconsiderationisemphasizedwithagray
background in the relative table and with a dashed line in the relative figure.


better separates these two attacks.  Incremental learning per-                    WINofthefirsttwopacketsandintheDIRof3rd (negativein-
formance could be affected by the shared use of ARP packets                       fluence) and 4th (positive influence) packets (Fig. 9b). Instead,
by both of them, potentially leading to overlapping patterns in                   IG poses more importance on the first WIN and 4th (positive)
traffic analysis despite serving different purposes.                              and 5th (negative) packets (Fig. 9e).  It is evident that while
   Finally,withinthecontextofTON-IoT(seeFig.8g),itisob-                           bothBiC andScratch misclassify Backdoor biflows withUp-
servedthattheInjectionattacksharesbehavioraltraitswiththe                         loading attacks, they make decisions relying on different sets
DDoS,Password,andXSSones. Conversely,Scratch(Fig.8h)                              of input fields. However, they share similarities in only the 2nd
correctly classifies the Injection attack. BiC confusion can be                   WIN and 4th DIR for SHAP, and the 1st WIN for IG.
due to the disruptive nature of such attacks, causing unusual                        In the latter case, the importance is assigned by SHAP (see
traffic spikes or abnormal request/response behaviors, which                      Fig. 9c) mostly to the first two WIN values and then spread
may be mistakenly identified as other types of attacks.                           across  the  PL  and  the  DIR  of  the  last  six  packets.    Con-
   In the following, we focus on the Edge-IIoT case, which                        versely, IG recognizes as the most influential input field the
exhibits the most critical performance scenarios forCnew. No-                     WIN (mostly of the 2nd packets) and the PL of the first two
tably,  we employ XAI techniques to gain insights into the                        packets to a lesser extent (Fig. 9f).
decision-making process.The three previously highlighted at-                         To quantify the coherence of explanations—i.e. the concor-
tacks also demonstrate low F1 in the Scratch model, with                          dance between the two input-attribution techniques—we com-
Backdooor achieving≈ 10%, DDoS ICMP Flood≈ 36%, and                               pute the Top5Ratio and Avg.Rel. (cf. Sec.4.1) of the explana-
Ransomware ≈  4%.   Since the last two exhibit comparable                         tions illustrated in Fig. 9. Notably, for Backdoor biflows mis-
or even better performance in the incremental and Scratch                         classified byBiC, the Top5Ratio is 80%, underscoring agree-
model, we focus our analysis on the Backdoor attack.                              ment between SHAP and IG regarding the most crucial fields
   Accordingly,weinvestigatetheinputimportancewithSHAP                            for decision-making.  Similarly, the two explanations exhibit
andIGforBackdoorbiflowsindifferentcasestounderstandthe                            an Avg.Rel. of≈5× 10−2, confirming only a slight difference
decision-making process (Fig. 9): (a) when they are confused                      betweenthetwomethods. ForScratch,inthecaseofmisclas-
with Uploading attack byBiC andScratch, (b) when they are                         sification,thetheTop5Ratiois6%whileAvg.Rel.is≈8×10−2.
correctly classified byScratch.                                                   Conversely,forthecorrectclassification,theTop5Ratiois40%
   In the former case, according to SHAP, the most influential                    while Avg.Rel. is≈9×10−2.
input fields forBiC are the WIN of 1st and 2nd packet and DIR                     Take-home:    In  conclusion,  poor  performance  for  spe-
from the 3nd packet to the 7th one (Fig. 9a). On the other hand,                  cific 0-day attacks can be influenced by their similarity to
although IG also identifies WIN and DIR as the most impor-                        previously-encountered attacks and further worsened by the
tant input fields, in this case, it only considers the first WIN                  incremental paradigm.  Furthermore, different input attribu-
and the directions of the 2nd, 3rd, 5th, and 7th packets (Fig. 9d).               tiontechniquesconsistentlyproducecoherentresultsforthe
For Scratch, SHAP identifies the most important fields in the                     incremental model while explanations have a weaker struc-
                                                                              17
```


### PDF page 18

[View original page, figures and tables](assets/page-018.png)

```text
SHAP:









      (a) Biflows confused withUploading byBiC              (b) Biflows confused withUploadingbyScratch                (c) Biflows correctly classified byScratch
                                                    IG:









     (d) Biflows confused withUploading byBiC               (e) Biflows confused withUploadingbyScratch                (f) Biflows correctly classified byScratch

Figure 9: Explanations for Backdoor biflows confused asUploading attack inEdge-IIoT by BiC (a, d) and Scratch (b, e) or correctly classified byScratch (c,
f) with SHAP (a,b,c) and IG (d,e, f).


tural similarity and greater variability with respect to the ex-                        of a DL model.  Notably, we investigate the impact of input
treme values for trained-from-scratchmodel.                                             perturbations on classification and detection performance.
                                                                                        We report corresponding performance under the different input
Table8: ClassificationanddetectionperformanceonCall forBiCandScratch                    perturbations forBiC andScratch in Tab. 8.
under varied perturbations of input data.  First row shows the absolute per-               Specifically, theslicing perturbation leads to poor classifica-
formance without perturbation for each dataset (in boldface).  The next rows
indicate the deviation from this baseline when perturbations are applied to the         tion(< 18%F1)anddetectionperformance(< 69%PAUC)for
input—lower values are the better (denoted by the   “Drop →” column).  Or-              both BiC and Scratch on the considered datasets.  This im-
ange cells indicate perturbation for which BiC and Scratch differs more than            plies that solely analyzing the initial phase of communication
5% while red text highlight perturbations with≥20% F1 Drop.
                                                                                        (viz. the first part of a biflow) does not suffice for the NIDS to
                               F1 Score [%]               PAUC [%]                      detect and classify an attack effectively.
          Perturbation       BiC       Scratch       BiC       Scratch                     Asfortheflippingmanipulation,thisdisruptionsignificantly
                   None     87.18        90.31        73.10        82.72                impacts classification performance,  with all datasets experi-
                                                                                        encing  a <  50%  F1,  particularly  evident  with Edge-IIoT
                Timeout       2.90       2.93       10.05       19.05                   with the incremental model (≈ 17%).  Furthermore, Scratch
                Jittering22            .74    18   .16        17.91    21   .96         achieves similar performance to BiC, even underperforming it
                Flipping     55.82      52.52       21.74       27.19                   on Edge-IIoT and TON-IoT. Detection performance also suf-
                 Slicing78          .38    80   .43 23.04       32.77
                   None     95.30        98.17        96.79        99.06                fers, falling below 60% PAUC for IoT-23 and IoT-NID, in
                                                                                        both Scratch and BiC.  Notably, in TON-IoT, BiC achieves
                Timeout       4.37       4.12        1.28        1.99                   a ≈ 68% PAUC, surpassing even Scratch (≈ 61% PAUC),
                Jittering     13.26        15.92          4.21          4.99            while on Edge-IIoT,  BiC achieves a ≈  73% PAUC while
                Flipping     64.42      72.93       29.38       37.65                   Scratch ≈ 79%.  These results suggest that packet direction
                 Slicing82          .33    80   .64    36   .62    37   .34             plays a significant role in attack classification for both incre-
                   None     97.42        98.61        87.10        94.16                mental and non-incremental models, while for detection, this
                Timeout       3.69       4.58       10.41        0.53                   holds across all datasets except Edge-IIoT, where Scratch
                Jittering       0.05            0              0.21          0.26       exhibits a smaller loss w.r.t. the unperturbed scenario.
                Flipping     77.22      68.98       32.98       35.52                      Ontheotherhand,forthetimeoutperturbation,theclassifica-
                 Slicing81          .93    79   .74 34.13       40.88                   tionperformanceisslightlyimpactedforIoT-23andIoT-NID
                   None     72.05        78.24        93.99        98.78                with −3% F1, and TON-IoT with −4% F1 w.r.t.   no pertur-
                Timeout      10.30      14.68       23.57       25.59                   bation case.  Instead, for Edge-IIoT we experience a −10%
                Jittering    25.35      40.11    30   .10    26   .66                   F1.   Concerning detection performance,  for TON-IoT it re-
                Flipping     54.70      65.74       21.06       20.26                   mains quite similar w.r.t.  the unperturbed scenario while all
                 Slicing     65.49      71.65    26   .98    30   .48                   the other datasets experience a significant decay−10% PAUC
                                                                                        forIoT-23 andIoT-NID, and−24% PAUC forEdge-IIoT.
6.2. Robustness                                                                            Regarding the jittering perturbation, for IoT-NID the classi-
                                                                                        fication performance is only slightly impacted suggesting that
Aim of the analysis:  In this section, we delve into the real-                          BiCreliesminimallyonIATfortheattackclassificationonthis
world implications of non-idealities associated with the input                          dataset. Thisisconfirmedalsobystabledetectionperformance.
                                                                                   18
```


### PDF page 19

[View original page, figures and tables](assets/page-019.png)

```text
(a) All classes                                    (b) Old classes                                (c) New classes
















                      (d) All classes                                    (e) Old classes                                 (f) New classes

               Figure 10: Analysis in a few-shot scenario of best configurations for leveraged datasets in terms of F1 (a,b,c) and PAUC (d,e, f).


Fortheotherdataset,theinter-arrivaltimebetweenconsecutive                      of BiC.  Additionally, the results include the performance at-
packets holds much greater significance in distinguishing be-                  tained when utilizing all available samples for the new attacks,
nign traffic from malicious traffic (with more than 10% decay                  denoted as “All Samples” in the figure legend.
w.r.t. unperturbed scenario).  This also holds for detection on                   With only 5 shots, the performance exhibits a notable dis-
IoT-23 and Edge-IIoT where a ≈ 18% and a ≈ 30% PAUC                            parity w.r.t. the “All Samples” scenario.   This difference is
degradationisexperienced. Conversely,forTON-IoTthedetec-                       mainly evident for new classes where we reach a ≈ 43% F1
tion performance remains quite stable suggesting that the IAT                  onEdge-IIoTandIoT-23,≈73%onIoT-NID,and≈68%on
is not significant in distinguishing benign and malicious traffic.             TON-IoT.
Take-home:    In  conclusion,   both  incremental  and  non-                      However, as the number of shots increases, the performance
incremental models are not robust to perturbation affecting                    of BiC improves consistently.  For IoT-23, the performance
thepacketdirectionandthenumberofvisiblepackets;how-                            surpassesthatoftheCILscenarioonce100shotsareemployed
ever, they show good performance against perturbations that                    for all subsets of classes (≈88% forCall andCold, ≈84% per
simulate packet loss or vary the packet inter-arrival time.                    Cnew), remaining quite stable at 200 shots.
                                                                                  Similarly,  in the Edge-IIoT domain,  performance at 25
6.3. Including few-shot 0-day attacks                                          shots is similar to that of the CIL scenario.  Specifically, the
Aim of the analysis:  A common challenge for NIDS lies in                      performancereaches≈73%forCall,≈74%forCold,and≈60%
gathering attack samples necessary to train ML and DL ap-                      forCnew. This stability persists up to 200 shots, where the per-
proaches,whichdemandsubstantialamountsofdatatoachieve                          formance reaches≈73% forCall andCold, and≈70% forCnew.
efficacy. In this section, we explore the efficacy of the optimal                 InthecaseofIoT-NID,theperformanceofFSCILscenarios
BiC configuration in an FSCIL scenario—where the incremen-                     is lower than the CIL one across all the shots’ numbers.  In
tal phase operates with a limited number of samples (referred                  particular, we obtain≈97% onCall,≈98% onCold, and≈89%
to as shots) for a newly detected 0-day attack.                                onCnew at 200 shots.
Precisely, we assess its performance across varying shot num-                     Lastly,  on TON-IoT,  performance begins to rise from 25
bers within the set K ∈{5,25,50,100,200}.  Furthermore, for                    shots onwards, matching and eventually surpassing the results
thisanalysis,wemadeslightadjustmentstoBiCconcerningthe                         obtained without any constraints on the samples of the new
composition percentage of samples inDcorr to ensure the pres-                  class (≈96% forCall andCold,≈89% forCnew). Notably, per-
enceoftrainingdata. Specifically,whenK < Nold,weconstruct                      formance slightly continues to improve for the Cold and Cnew
the correction dataset using⌈10%· K⌉ samples. Conversely, in                   subsets, reaching≈97% forCall andCold, and≈93% forCnew
caseswhereK≥ Nold,weemploytheoriginalBiCformulation.                           at 200 shots.
  ThefindingsfromthisanalysisaredepictedinFig.10,show-                            As for detection, the performance exhibits a unimodal trend,
casing the performance achieved by the optimal configuration                   peaking at a specific point for each dataset (i.e., 50 shots for
                                                                           19
```


### PDF page 20

[View original page, figures and tables](assets/page-020.png)

```text
Edge-IIoT, 100 for IoT-23, 200 for IoT-NID, and 25 for                          (resp. Scratch) without perturbation. Conversely, both mod-
TON-IoT).   Generally, the performances achieved under the                      els struggle with perturbations affecting packet direction and
few-samples constraint surpass those of the CIL model.  This                    limiting packet visibility—obtaining at most F1 performance
is probably due to the reduced catastrophic forgetting experi-                  < 10%and≈37%PAUCdropforbothBiCandScratch. Fur-
enced by the model.                                                             thermore, across all perturbations, BiC and Scratch exhibit
Take-home:  These findings highlight the significant impact                     comparabledropsinperformance,exceptforEdge-IIoTinthe
of low shot numbers (i.e.  5 and 15) on classification per-                     classificationtaskandIoT-23inthedetectiontask,wheretheir
formance, with noticeable improvements observed as the shot                     performance differs by more than 5%.
numberincreases(from50onwards),effectivelymitigatingim-                            Lastly, to address the scarcity of samples in real-world sce-
balanceissuesandenhancingoverallperformance.Conversely,                         narios, we tested our solution with constraints on number of
detection performance shows an unimodal trend and re-                           samples available.   We found that (A5) classification perfor-
mainseffectiveunderfew-sampleconstraints,outperforming                          mance is affected with very few samples (i.e. 5 and 15 for new
the CIL model.                                                                  attacks)whileforhighnumberstheyreachorevensurpassCIL
                                                                                (viz.  all samples) scenario.  On the other hand, detection per-
                                                                                formance is not affected by the fewness of samples exhibiting
7. Conclusion                                                                   stronger performance w.r.t. the all samples scenario.
                                                                                   As future directions, we will delve into further meaningful
  TheIoTrapidgrowthbringsenhancedconnectivityandcon-                            evaluation scenarios within the specified domain, also evalu-
venience but also significant cybersecurity challenges.   With                  ating the generalization capability of a NIDS when deployed
malicious actors targeting IoT vulnerabilities, the need for re-                in different networks.Our focus extends to exploring the ap-
silient security measures is crucial. CIL offers a dynamic strat-               plication of multimodal deep learning architectures, to lever-
egy empowering ML and DL models to evolve and adapt to                          age the diversity inherent in network traffic to optimize the ef-
emerging attack patterns while detecting known threats effec-                   fectiveness of CIL approaches, or more sophisticated CIL ap-
tively.  This approach holds promise for strengthening NIDS                     proaches [44, 53].This includes considering the payload data
resilience in IoT networks.                                                     as DL input, particularly in scenarios where privacy concerns
  In this study, we tackled research questions (Q1-Q5) related                  allowitsusage[48].Furthermore,wearekeenoninvestigating
to NIDS challenges in real-world scenarios, providing answers                   CIL solutions that dynamically adapt to notable shifts in net-
to each (A1-A5).  We evaluated the effectiveness of cutting-                    work traffic patterns, as highlighted in [54]. This adaptive ap-
edge CIL approaches in detecting & classifying 0-day attacks.                   proach aims to accommodate variations arising from changes
Notably, (A1) BiC emerges as the top performer in detecting                     in attacker behavior or the emergence of new threat variants,
(viz. binary misuse detection) and classifying (viz. attack clas-               effectively mitigating intra-class concept-drift.
sification)inanincrementalsetup,exhibitingatmost≈18%F1
dropand≈19%PAUCdropw.r.t. atrained-from-scratchmodel                            Acknowledgment
but saving up to≈80% of its training time. Additionally, (A2)
adjustingkeyhyper-parametersleadstoimprovedperformance                             This work is partially supported by the Italian PNRR MUR
for adaptive NIDS, obtaining up to≈18% improvement in F1                        “Centro  Nazionale  HPC,  Big  Data  e  Quantum  Computing,
and≈15% in PAUC, fostering the adoption of this incremental                     Spoke9  -  Digital  Society  &  Smart  Cities”;  in  part  by  the
solution in real-world environments.                                            “xInternet” Project––funded by MUR—within the PRIN 2022
  Then, we dealt with practical hurdles for NIDS, such as ex-                   program (D.D.104-02/02/2022); and in part by the European
plainability, robustness, and few-sample availability.                          Union under the Italian National Recovery and Resilience Plan
  Specifically,(A3)weinvestigatedthesubparperformanceof                         (NRRP) of NextGenerationEU, partnership on “Telecommuni-
certain 0-day attacks with XAI techniques.  We identified the                   cations of the Future” (PE00000001 - program “RESTART”).
cause of this performance issue mainly in the similarities be-                  This manuscript reflects only the authors’ views and opinions
tween the 0-day attacks and already encountered ones but also                   and the Ministry cannot be considered responsible for them.
further degradation is due to the incremental paradigm. More-
over,wevalidatedtheexplanationsobtainedfromdifferentfea-
ture attribution techniques (i.e. SHAP and IG). We confirmed                    References
the coherence in the outcomes of these two methods for the in-
cremental model (Top5Ratio=80% and Avg.Rel.=5× 10−2).                             [1]Jayavardhana Gubbi, Rajkumar Buyya, Slaven Marusic, and Marimuthu
Conversely, for trained-from-scratch model, explanations have                         Palaniswami. Internet of Things (IoT): A vision, architectural elements,
a weaker structural similarity (Avg.Rel.≥8×10−2), and higher                          andfuturedirections. FutureGenerationComputerSystems,29(7):1645–
variability regarding the extreme values (Top5Ratio≥40%).                             1660, 2013.
                                                                                  [2]Fadele  Ayotunde  Alaba,  Mazliza  Othman,  Ibrahim  Abaker  Targio
  As   for   robustness,   (A4)   both   incremental   and   non-                     Hashem,andFaizAlotaibi. InternetofThingssecurity: Asurvey. Journal
incremental models maintain satisfactory performance to in-                           of Network and Computer Applications, 88:10–28, 2017.
putperturbationaffectinginter-arrivaltimeorsimulatingpacket                       [3]Ciro Guida, Alfredo Nascita, Antonio Montieri, and Antonio Pescap    ´e.
loss. For instance, they experience at most≈25% (resp. ≈40)                           Cross-evaluation of deep learning-based network intrusion detection sys-
                                                                                      tems. InIEEE10thInternationalConferenceonFutureInternetofThings
F1 drop and ≈ 30% (resp.  ≈ 27%) PAUC drop w.r.t.   BiC                               and Cloud (FiCloud), 2023.
                                                                            20
```


### PDF page 21

[View original page, figures and tables](assets/page-021.png)

```text
[4]GiampaoloBovenzi,GiuseppeAceto,DomenicoCiuonzo,AntonioMon-                                           threats. In IEEE International Conference on Big Data (BigData), pages
      tieri, Valerio Persico, and Antonio Pescap´e. Network anomaly detection                            3547–3555, 2023.
      methods in IoT environments via deep learning:  A fair comparison of                        [24]Giampaolo  Bovenzi,  Alfredo  Nascita,  Lixuan  Yang,  Alessandro  Fi-
      performance and robustness. Computers& Security, 128:103167, 2023.                                 namore,  Giuseppe Aceto,  Domenico Ciuonzo,  Antonio Pescap´e,  and
 [5]YangGuo.Areviewofmachinelearning-basedzero-dayattackdetection:                                       Dario Rossi.  Benchmarking class incremental learning in deep learning
      Challenges and future directions. Computer Communications, 198:175–                                traffic classification.  IEEE Trans. Netw. Service Manag., 21(1):51–69,
      185, 2023.                                                                                         2024.
 [6]Idio Guarino, Giampaolo Bovenzi, Davide Di Monda, Giuseppe Aceto,                             [25]Idio Guarino, Chao Wang, Alessandro Finamore, Antonio Pescap      `e, and
      Domenico Ciuonzo, and Antonio Pescap´e. On the use of machine learn-                               Dario Rossi. Many or few samples? comparing transfer, contrastive and
      ing approaches for the early classification in network intrusion detec-                            meta-learning in encrypted traffic classification. InIFIP Traffic Monitor-
      tion. In IEEE International Symposium on Measurements& Networking                                  ing Analysis (TMA), 2023.
      (M&N), pages 1–6, 2022.                                                                     [26]Jielun  Zhang,  Fuhao  Li,  Feng  Ye,  and  Hongyu  Wu.    Autonomous
 [7]Tingting Wang, Qiujian Lv, Bo Hu, and Degang Sun.  A few-shot class-                                 unknown-application filtering and labeling for DL-based traffic classifier
      incremental learning approach for intrusion detection.   In IEEE Inter-                            update. InIEEEConferenceonComputerCommunications(INFOCOM),
      national Conference on Computer Communications and Networks (IC-                                   2020.
      CCN), pages 1–8, 2021.                                                                      [27]ZhizhongLiandDerekHoiem. Learningwithoutforgetting.       IEEETrans.
 [8]Sebastian Garcia, Agustin Parmisano, and Maria Jose Erquiaga. IoT-23:                                Pattern Anal. Mach. Intell., 40(12):2935–2947, 2017.
      A labeled dataset with malicious and benign IoT network traffic, 2020.                      [28]J.Kirkpatrick,R.Pascanu,N.Rabinowitz,J.Veness,G.Desjardins,A.A.
      URLhttps://www.stratosphereips.org/datasets-iot23.                                                 Rusu, K. Milan, J. Quan, T. Ramalho, A. Grabska-Barwinska, D. Hass-
 [9]Tim M Booij,  Irina Chiscop,  Erik Meeuwissen,  Nour Moustafa,  and                                  abis, C. Clopath, D. Kumaran, and R. Hadsell. Overcoming catastrophic
      Frank TH den Hartog. ToN          IoT: The role of heterogeneity and the need                      forgettinginneuralnetworks. InProceedingsoftheNationalAcademyof
      for standardization of features and attack types in IoT network intrusion                          Sciences (PNAS), 2017.
      datasets. IEEE Internet Things J., 2021.                                                    [29]Francisco M Castro, Manuel J Mar      ´ın-Jim´enez, Nicol´as Guil, Cordelia
[10]Hyunjae  Kang,  Dong  Hyun  Ahn,  Gyung  Min  Lee,  Jeong  Do  Yoo,                                  Schmid,andKarteekAlahari. End-to-endincrementallearning. InEuro-
      KyungHoPark,andHuyKangKim. IoTnetworkintrusiondataset,2019.                                        pean Conference on Computer Vision (ECCV), pages 233–248, 2018.
      URLhttps://dx.doi.org/10.21227/q70p-q449.                                                   [30]Yue Wu, Yinpeng Chen, Lijuan Wang, Yuancheng Ye, Zicheng Liu, Yan-
[11]Mohamed Amine Ferrag, Othmane Friha, Djallel Hamouda, Leandros                                       dong Guo, and Yun Fu. Large scale incremental learning. In IEEE/CVF
      Maglaras, and Helge Janicke.  Edge-IIoTset: A new comprehensive re-                                Conference on Computer Vision and Pattern Recognition (CVPR), pages
      alistic cyber security dataset of IoT and iIoT applications for centralized                        374–382, 2019.
      and federated learning. IEEE Access, 10:40281–40306, 2022.                                  [31]Saihui Hou, Xinyu Pan, Chen Change Loy, Zilei Wang, and Dahua Lin.
[12]Kalle Burbeck and Simin Nadjm-Tehrani.  Adaptive real-time anomaly                                   Learning a unified classifier incrementally via rebalancing. InIEEE/CVF
      detectionwithincrementalclustering. InformationSecurityTechnicalRe-                                Conference on Computer Vision and Pattern Recognition (CVPR), 2019.
      port, 12(1):56–67, 2007.                                                                    [32]Giampaolo  Bovenzi,  Lixuan  Yang,  Alessandro  Finamore,  Giuseppe
[13]Cheng Zhong and Na Li.  Incremental clustering algorithm for intrusion                               Aceto, Domenico Ciuonzo, Antonio Pescap`e, and Dario Rossi.  A first
      detectionusingclonalselection. InIEEEPacific-AsiaWorkshoponCom-                                    look at class incremental learning in deep learning mobile traffic classifi-
      putational Intelligence and Industrial Application (PACIIA), volume 1,                             cation. InIFIP Traffic Monitoring Analysis (TMA), 2021.
      pages 326–331, 2008.                                                                        [33]Marc Masana, Xialei Liu, Bartłomiej Twardowski, Mikel Menta, An-
[14]Wei-Yi Yu and Hahn-Ming Lee. An incremental-learning method for su-                                  drew D Bagdanov, and Joost van de Weijer. Class-incremental learning:
      pervised anomaly detection by cascading service classifier and ITI de-                             survey and performance evaluation on image classification. IEEE Trans.
      cision tree methods.  In Springer Intelligence and Security Informatics:                           Pattern Anal. Mach. Intell., 45(5):5513–5533, 2023.
      Pacific Asia Workshop (PAISI), pages 155–160, 2009.                                         [34]Sylvestre-Alvise  Rebu     ffi,   Alexander  Kolesnikov,   Georg  Sperl,   and
[15]YangYi,JianshengWu,andWeiXu. IncrementalSVMbasedonreserved                                           Christoph H Lampert.  iCaRL: incremental classifier and representation
      setfornetworkintrusiondetection. ExpertSystemswithApplications,38                                  learning.   In IEEE/CVF Conference on Computer Vision and Pattern
      (6):7698–7707, 2011.                                                                               Recognition (CVPR), pages 2001–2010, 2017.
[16]BinhanXu,ShuyuChen,HancuiZhang,andTianshuWu. Incrementalk-                                    [35]Minsoo Kang, Jaeyoo Park, and Bohyung Han. Class-incremental learn-
      NN SVM method in intrusion detection. In IEEE 8th International Con-                               ing by knowledge distillation with adaptive feature consolidation.   In
      ference on Software Engineering and Service Science (ICSESS), pages                                IEEE/CVF  Conference  on  Computer  Vision  and  Pattern  Recognition
      712–717, 2017.                                                                                     (CVPR), pages 16071–16080, 2022.
[17]Christos Constantinides, Stavros Shiaeles, Bogdan Ghita, and Nicholas                         [36]LloydSShapley.Avalueforn-persongames.       ContributionstotheTheory
      Kolokotronis.  A novel online incremental learning intrusion prevention                            of Games, 2(28):307–317, 1953.
      system.   In IFIP 10th International Conference on New Technologies,                        [37]Mukund Sundararajan, Ankur Taly, and Qiqi Yan. Axiomatic attribution
      Mobility and Security (NTMS), pages 1–6, 2019.                                                     for deep networks. In 34th PMLR International Conference on Machine
[18]Mahendra Data and Masayoshi Aritsugi.  An incremental learning algo-                                 Learning (ICML), volume 70, pages 3319–3328, 2017.
      rithm on imbalanced data for network intrusion detection systems.   In                      [38]Scott M Lundberg and Su-In Lee.   A unified approach to interpreting
      ACM 10th International Conference on Computer and Communications                                   modelpredictions. In30thConferenceonNeuralInformationProcessing
      Management (ICCCM), pages 191–199, 2022.                                                           Systems (NeurIPS), volume 30, pages 4765–4774, 2017.
[19]Hao Xu and Yongjun Wang.  A continual few-shot learning method via                            [39]AlfredoNascita,AntonioMontieri,GiuseppeAceto,DomenicoCiuonzo,
      meta-learning for intrusion detection.   In IEEE 4th International Con-                            Valerio Persico, and Antonio Pescap´e. XAI meets mobile traffic classifi-
      ference on Civil Aviation Safety and Information Technology (ICCASIT),                             cation: Understandingandimprovingmultimodaldeeplearningarchitec-
      pages 1188–1194, 2022.                                                                             tures. IEEE Trans. Netw. Service Manag., 18(4):4225–4246, 2021.
[20]Alec F Diallo and Paul Patras.  Cluster and conquer:  Malicious tra     ffic                  [40]Meike Nauta, Jan Trienes, Shreyasi Pathak, Elisa Nguyen, Michelle Pe-
      classification at the edge. IEEE Trans. Netw. Service Manag., 2023.                                ters, Yasmin Schmitt, J¨org Schl¨otterer, Maurice van Keulen, and Christin
[21]Lei Du, Zhaoquan Gu, Ye Wang, Le Wang, and Yan Jia.   A few-shot                                     Seifert.  From anecdotal evidence to quantitative evaluation methods: A
      class-incremental learning method for network intrusion detection. IEEE                            systematic review on evaluating explainable AI.  ACM Computing Sur-
      Trans. Netw. Service Manag., 21(2):2389–2401, 2024.                                                veys, 55(13s):1–42, 2023.
[22]Zhuoxue Song, Ziming Zhao, Fan Zhang, Gang Xiong, Guang Cheng,                                [41]Amani Abou Rida, Rabih Amhaz, and Pierre Parrend. Metrics for evalu-
      Xinjie Zhao, Shize Guo, and Binbin Chen.  I2RNN: an incremental and                                atinginterfaceexplainabilitymodelsforcyberattackdetectioninIoTdata.
      interpretable recurrent neural network for encrypted traffic classification.                       InSpringer Complex Computational Ecosystems (CCE), 2023.
      IEEE Trans. Depend. Sec. Comput., 2023.                                                     [42]Amir Mahdi Sadeghzadeh, Saeed Shiravi, and Rasool Jalili. Adversarial
[23]Francesco   Cerasuolo,   Giampaolo   Bovenzi,   Christian   Marescalco,                              networktraffic: Towardsevaluatingtherobustnessofdeep-learning-based
      Francesco Cirillo, Domenico Ciuonzo, and Antonio Pescap`e.  Adaptive                               network traffic classification. IEEE Trans. Netw. Service Manag., 18(2):
      intrusiondetectionsystems: ClassincrementallearningforIoTemerging
                                                                                             21
```


### PDF page 22

[View original page, figures and tables](assets/page-022.png)

```text
1962–1976, 2021.                                                                           [49]Giuseppe Aceto, Domenico Ciuonzo, Antonio Montieri, and Antonio
[43]ChaoWang,AlessandroFinamore,PietroMichiardi,MassimoGallo,and                                        Pescap´e. Mobile encrypted traffic classification using deep learning: Ex-
      Dario Rossi.   Data augmentation for traffic classification.   In Springer                        perimentalevaluation,lessonslearned,andchallenges.IEEETrans.Netw.
      International Passive and Active Measurement Conference (PAM), pages                              Service Manag., 16(2):445–458, 2019.
      159–186, 2024.                                                                             [50]Giuseppe Aceto, Domenico Ciuonzo, Antonio Montieri, and Antonio
[44]Francesco Cerasuolo, Alfredo Nascita, Giampaolo Bovenzi, Giuseppe                                   Pescap`e.  MIMETIC: mobile encrypted traffic classification using mul-
      Aceto, Domenico Ciuonzo, Antonio Pescap`e, and Dario Rossi.   ME-                                 timodal deep learning. Computer Networks, 165:106944, 2019.
      MENTO: A novel approach for class incremental learning of encrypted                        [51]Alfredo Nascita,  Francesco Cerasuolo,  Davide Di Monda,  Jonas Th-
      traffic. Computer Networks, page 110374, 2024.                                                    ernAberiaGarcia,AntonioMontieri,andAntonioPescap`e. Machineand
[45]Franc¸ois De Keersmaeker,  Yinan Cao,  Gorby Kabasele Ndonda,  and                                  deep learning approaches for IoT attack classification.  In IEEE Confer-
      Ramin Sadre.  A survey of public IoT datasets for network security re-                            ence on Computer Communications Workshops (INFOCOM WKSHPS),
      search. IEEE Commun. Surveys Tuts., 2023.                                                         pages 1–6, 2022.
[46]BarjinderKaur,SajjadDadkhah,FarzanehShoeleh,EuclidesCarlosPinto                              [52]Manuel Lopez-Martin, Belen Carro, Antonio Sanchez-Esguevillas, and
      Neto, Pulei Xiong, Shahrear Iqbal, Philippe Lamontagne, Suprio Ray,                               Jaime Lloret. Network traffic classifier with convolutional and recurrent
      and Ali A Ghorbani. Internet of Things (IoT) security dataset evolution:                          neural networks for Internet of Things.  IEEE Access, 5:18042–18050,
      Challenges and future directions. Internet of Things, 22:100780, 2023.                            2017.
[47]Christin Alex,  Giselle Creado,  Wesam Almobaideen,  Orieb Abu Al-                           [53]WenbinZhu,XiuliMa,YanliangJin,andRuiWang. ILETC:Incremental
      ghanam,  and Maha Saadeh.    A comprehensive survey for IoT secu-                                 learning for encrypted traffic classification using generative replay and
      rity datasets taxonomy, classification and machine learning mechanisms.                           exemplar. Computer Networks, 224:109602, 2023.
      Computers& Security, 132:103283, 2023.                                                     [54]OmarAbdelWahab. IntrusiondetectionintheIoTunderdataandconcept
[48]Giampaolo Bovenzi, Giuseppe Aceto, Domenico Ciuonzo, Valerio Per-                                   drifts: Online deep learning approach.  IEEE Internet Things J., 9(20):
      sico, and Antonio Pescap´e. A hierarchical hybrid intrusion detection ap-                         19706–19716, 2022.
      proach in IoT scenarios. In IEE GLOBECOM’20, pages 1–7, 2020.















































                                                                                            22
```
