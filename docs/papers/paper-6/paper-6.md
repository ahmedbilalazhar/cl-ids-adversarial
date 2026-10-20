# CND-IDS: Continual Novelty Detection for Intrusion Detection Systems

**Authors:** Sean Fuhrman; Onat Gungor; Tajana Rosing

**Publication:** 2025 62nd ACM/IEEE Design Automation Conference (DAC) (2025).

**Publication DOI:** https://doi.org/10.1109/DAC63849.2025.11132541

**Verified free PDF:** https://arxiv.org/pdf/2502.14094

**Downloaded version:** arXiv author version v1; independently verified DAC 2025 proceedings publication. The arXiv posting alone is not the peer-review evidence.

**Qualification:** Premier peer-reviewed proceedings, ACM/IEEE DAC 2025; no journal quartile. Journal rankings use the 2024 JIF category quartile (June 2025 JCR), not an asserted 2026 ranking.

**Integrity:** 7 pages; 442,271 bytes; SHA-256 `3ec29fe0e070f3228efbd74c75f1c0ad04f747982947ba833678705d2058c8d7`. Verified 8 October 2026.

## Reading and extraction note

The PDF is the authoritative complete manuscript. Below is automatic page-level text extraction, not a newly authored summary or a verbatim-quality transcription. Two-column order, formulas, ligatures and table spacing can be imperfect. Every page has a rendered PNG in `assets/` for inspecting figures, equations and tables at their original locations. Publication metadata is saved alongside the images. The technical review is in [the selection audit](../phase2-selection-audit.md).

## Full manuscript text


### PDF page 1

[View original page, figures and tables](assets/page-001.png)

```text
CND-IDS: Continual Novelty Detection for
                                   Intrusion Detection Systems

                                         Sean Fuhrman1, Onat Gungor2, and Tajana Rosing2

               1Department of Electrical and Computer Engineering, University of California, San Diego
                2Department of Computer Science and Engineering, University of California, San Diego
                                                  {stfuhrma, ogungor, tajana}@ucsd.edu


  Abstract—Intrusion  detection  systems  (IDS)  play  a  crucial
role  in  IoT  and  network  security  by  monitoring  system  data
and  alerting  to  suspicious  activities.  Machine  learning  (ML)
has  emerged  as  a  promising  solution  for  IDS,  offering  highly
accurate intrusion detection. However, ML-IDS solutions often
overlook two critical aspects needed to build reliable systems:
continually changing data streams and a lack of attack labels.
Streaming  network  traffic  and  associated  cyber  attacks  are
continually  changing,  which  can  degrade  the  performance  of
deployed  ML  models.  Labeling  attack  data,  such  as  zero-day
attacks, in real-world intrusion scenarios may not be feasible,
making the use of ML solutions that do not rely on attack labels
necessary. To address both these challenges, we propose CND-
IDS, a continual novelty detection IDS framework which consists
of(i)alearning-basedfeatureextractorthatcontinuouslyupdates                   Fig. 1: State of the art machine learning intrusion detection
new feature representations of the system data, and (ii) a novelty                        performance on known/unknown attacks
detector that identifies new cyber attacks by leveraging principal
componentanalysis(PCA)reconstruction.Ourresultsonrealistic
intrusion datasets show that CND-IDS achieves up to 6.1× F-
score improvement, and up to 6.5× improved forward transfer                  in the data stream distribution, and CL models are designed
over the SOTA unsupervised continual learning algorithm. Our                 to function well across multiple experiences. This capability
code will be released upon acceptance.                                       is currently essential in cybersecurity, where each new attack
                         I.  INTRODUCTION                                    type can be considered as a new experience [7]. To illustrate,
                                                                             an intrusion detection model trained for a group of attacks
  In today’s digital landscape, cybersecurity is essential for               (experiences) such as worm, shellcode, and exploits should be
safeguarding  sensitive  data  and  maintaining  trust  in  digital          able to identify new types of attacks (experiences) such as
systems.  With  cyber  threats  becoming  more  sophisticated,               backdoor and fuzzers [8]. Some studies have adopted CL for
organizationsmustadoptthoroughsecuritymeasurestoprotect                      intrusion detection [7]–[12], but they rely on labeled attack
against breaches and unauthorized access [1]. A critical part of             data, which may not always be feasible to obtain. This causes
such security measures are intrusion detection systems (IDS)                 the ML model to overfit to common attacks in the dataset,
which identify malicious network traffic and computer usage                  resulting in a failure to detect rare and zero-day threats.
[2]. Recently, Machine Learning (ML) has become a popular                       SOTA ML-IDS solutions have been shown to have high
IDS solution due to its great attack detection performance and               accuracy on well represented attacks within the data, however
less requirement for human knowledge [3]. However, state-                    have low precision on infrequent attacks [13]. It is extremely
of-the-art (SOTA) ML-IDS solutions often fail to adequately                  difficult for zero-day attacks to be well represented in the data.
address the challenges posed by (i) the evolving nature of                   Figure 1 illustrates the limitations of current ML-IDS methods
cyber attacks and (ii) the lack of attack labels.                            in handling zero-day attacks, revealing a substantial decline in
  A University of Maryland survey predicts that a new cyber                  performance when faced with previously unseen threats. To
attack happens somewhere on the Internet every 39 seconds                    address this issue, novelty detection (ND)-based ML methods
[4], underscoring the need for dynamic IDS. However, most                    havedemonstratedsignificantpromiseindetectingbothknown
SOTA ML-IDS approaches are static (offline) and cannot eas-                  and zero-day attacks without requiring a labeled dataset [14].
ilyadapttheirbehaviorovertime[5].MLmodels,whentaught                         These ND solutions can effectively identify attacks by ana-
new  knowledge,  catastrophically  forget  previously  known                 lyzing purely normal data, provided that the attacks exhibit
information.  To  efficiently  address  this  problem,  continual            substantial deviations from normal behavior [14]. However,
learning(CL)isproposedwhichiscapableoflearningfroman                         it  has  been  shown  that  ND  algorithms  such  as  Isolation
infinite stream of data [6]. An experience is defined as a shift             Forest  and  Local  Outlier  Factor  result  in  lower  prediction
```


### PDF page 2

[View original page, figures and tables](assets/page-002.png)

```text
Fig. 2: Continual Novelty Detection IDS (CND-IDS) Framework


performance under changing environments, where they suffer                    models to acquire new information while minimizing the loss
from issues like catastrophic forgetting [15]. This issue can be              of previously learned knowledge. Prasath et al. [9] highlight
addressed by leveraging continual learning strategies, hence                  that intrusion datasets exhibit these shifting distributions, un-
motivating continual novelty detection methods for IDS.                       derscoringtheneedforCL-capableIDSthatcanautonomously
  To  address  the  challenges  of  evolving  data  streams  and              adapt to the evolving characteristics of the data. Few studies
lack of supervision, we propose CND-IDS, a continual novelty                  have recently adopted CL for intrusion detection. Kozik et
detection approach for ML-based intrusion detection (Fig. 2).                 al.  [7]  extend  efficient  lifelong  learning  algorithm  [19]  to
To the best of our knowledge, we are the first to propose                     detect cyber attacks and address the data imbalance problem.
continual ND for intrusion detection. CND-IDS consists of                     Kumar et al. [20] applied Elastic Weight Consolidation and
two critical components: a continual feature extractor (CFE)                  Gradient  Episodic  Memory  CL  algorithms.  In  a  follow-up
and a novelty detector based on principal component analysis                  study [10], they extend a memory-based CL method and pro-
(PCA) reconstruction. We design a novel continual ND loss                     posed a novel approach (perturbation assistance for parameter
to learn representations of the data stream, enabling the CFE                 approximation),  improving  CL  scalability.  Nevertheless,  all
to update its representations in a streaming environment with                 of these studies leverage labeled attack data to devise their
zero attack labels. PCA reconstruction error is then used to                  CL solutions, which may not be feasible in IDS due to the
classify test samples as either attack or normal data based                   difficulty and expense of obtaining such labeled data.
on thresholding. By fitting PCA on normal data, CND-IDS is                       Continual Novelty Detection:ContinualNoveltyDetection
trained without any labeled attack data, enabling it to detect                (CND) primarily addresses detecting distribution shifts after
previously unknown zero-day attacks. Our results show that                    ML model deployment. To illustrate, Kim et al. [21] highlight
on realistic intrusion datasets, CND-IDS achieves up to 6.1×                  how ND combined with CL is necessary for realistic class
F-score improvement over the SOTA unsupervised continual                      incremental learning. Aljundi et al. [22] investigate CND for
learning algorithm.                                                           detecting data outside the current model’s knowledge. Finally,
                        II.  RELATED WORK                                     Rios et al. [23] propose a novel CND framework for detecting
                                                                              new data and incorporating it into the current ML model’s
  Intrusion Detection Systems: Intrusion Detection Systems                    knowledge. These studies focus on using ND to identify data
(IDS)  fall  into  two  main  categories:  Signature-based  and               outside the training set and integrate it into the ML model
Anomaly-based IDS. Signature-based IDS identify attacks by                    via  CL  strategies.  However,  Faber  et  al.  [15]  demonstrate
matching network data to known attack patterns. In contrast,                  the performance decline in ND-algorithms themselves under
Anomaly-based IDS use machine learning methods to analyze                     continual  learning  settings.  Given  the  constantly  changing
statistical properties of network data [16]. Machine learning-                nature  of  attacks,  it  is  necessary  for  ML-IDS  systems  to
based IDS (ML-IDS), a popular form of Anomaly-based IDS,                      continually adapt without labels, which motivates our work.
use historical data to train models, enhancing accuracy and                   To the best of our knowledge, we are the first to propose
reducing the need for expert knowledge [17]. The literature                   continual novelty detection for ML-based intrusion detection.
proposes  various  ML  models,  including  supervised  models                                    III.  CND-IDS FRAMEWORK
such as support vector machine, random forest, deep neural
networks [18], and unsupervised models like isolation forest,                    Fig. 2 illustrates our continual novelty detection-based in-
autoencoder, and principal component analysis [14].                           trusion  detection  (CND-IDS)  framework.  We  first  apply  a
  ContinualLearningforIntrusionDetection:CurrentML-                           continual learning data preparation phase, where we divide the
IDS solutions are often built on the premise that all data are                intrusion data into normal data, training experiences, and test
sampled  i.i.d.  (independent  and  identically  distributed)  [5],           experiences.Ourframeworkconsistsoftwomaincomponents:
makingthemvulnerabletoperformancedegradationwhendata                          a continual feature extractor (CFE) and principal component
distributions shift. Continual Learning (CL) seeks to train ML                analysis  (PCA)-based  novelty  detector.  The  CFE  creates  a
```


### PDF page 3

[View original page, figures and tables](assets/page-003.png)

```text
representation of the data that is used to distinguish normal                  Algorithm 1 CND-IDS Algorithm (Training and Test)
and attack data by the novelty detector. The CFE allows the                    Require: E - Experience Set; Nc - Subset of Clean Normal
model to learn new feature representations overtime, so that it                     Data; CFE  - Continual Feature Extractor; ND - PCA
can easily adapt as new attacks are introduced through the                          Novelty Detector
data  stream.  CFE  is  trained  through  our  continual  novelty               1: for i← 1 to|E| do
detection loss function, to continually learn from the input                    2:       Get Xtrain from experience data Ei
stream without forgetting. The next component, PCA recon-                       3:       Fit CFE to training data Xtrain
struction, provides an anomaly score on the feature output                      4:       Encode Nc by passing it through CFE
from the feature extractor. PCA is trained purely on normal                     5:       Fit ND to encoded Nc
data, therefore it can generalize well to unseen attacks. Finally               6:       Get Xtest,Ytest from all experiences within E
we apply a threshold, τ, such that if the anomaly score is                      7:       Encode Xtest by passing it through CFE
greater than τ, we classify that data as an attack. Overall, our                8:       Use ND to compute anomaly score Stest on test data
learning framework does not require any labeled attack data.                    9:       Compute threshold τ based on thresholding method
A. Continual Learning (CL) Data Preparation                                    10:       Compute predictions such that Ypred = (Stest >τ)
                                                                               11:       Compute evaluation metrics based on Ypred,Ytest
  We assume a given dataset contains attack data A, normal                     12: end for
(benign) data N, and various attack types C. To begin our
data  preparation,  we  remove  10%  of  the  normal  data,  and
save  this  as  clean  normal  data Nc  to  train  PCA  novelty                At the end of each training experience, we evaluate on the
detector. For the remaining data, we split it across an arbitrary              test  set  of  all  experiences.  Therefore,  we  evaluate  model
number of experiences m. We create a set of experiences E,                     performance on unseen attacks (future experiences) and seen
such that each individual experience is (E0,E1,...Em). Each                    attacks (past experiences). When evaluating a batch of testing
experience contains a portion of the remaining normal data,                    data, we encode all points from Xtest with CFE. Then use
of  size   0.9∗|N|m    .  The  attacks  are  distributed  such  that  each     PCA reconstruction to get an anomaly score Stest  for each
experience  contains  |C|m   different  attack  classes.  Therefore,           point  based  on  the  reconstruction  loss.  Next,  we  leverage
each experience contains some number of unique attacks to                      widely used Best-F [24] to select a thresholdτ. Ultimately, all
that experience. This allows us to test on zero-day attacks                    anomaly scores greater thanτ are classified as attack while all
throughfutureexperiences,andseenattacksthroughcurrentor                        scores less than or equal toτ are classified as normal, resulting
past experiences. Each experience Ei is split into training and                in the CND-IDS predictions Ypred. We ultimately compute our
testing set. The training split contains onlyXtrain data points,               evaluation metricsby comparingYpred with the true labelsYtest.
meaning it does not include any labels. The test data contains                 C. Continual Feature Extractor (CFE)
{Xtest,Ytest} where Ytest ∈ {0,1}, where 0 means normal,
and1meansattackdata.ForeachexperienceEi,weutilizethe                              CFE  is  an  autoencoder  (AE)-based  model  that  leverages
trainingsetXitrain andNc totrainCND-IDS.Wethenevaluate                         Multi-Layer Perceptron (MLP) as both the encoder and de-
the model using the test points {Xtest,Ytest}. This setup is                   coder. Our continual novelty detection loss (LCND) consists
designed to represent a realistic intrusion detection scenario,                of a novel cluster separation loss (LCS), a reconstruction loss
where attacks are entirely unknown before deployment into a                    (LR), and a continual learning loss (LCL):
continual learning environment. In our framework, the only
known data is N, while all attack data is unlabeled. With this                                LCND =LCS +λRLR+λCLLCL                (1)
data setup, we can assess model’s performance across various
attack  scenarios.  Specifically,  we  can  simulate  the  model’s                where λR ∈ [0,1] and λCL ∈ [0,1] are hyper-parameters
response to zero-day attacks as well as known attacks.                         controlling  the  strength  of  the  reconstruction  loss  and  the
B. Proposed Algorithm                                                          continual learning loss respectively.
                                                                                  Cluster Separation Loss: We design a novel cluster sepa-
  Algorithm  1  depicts  the  proposed  CND-IDS  algorithm,                    ration lossLCS to enhance the performance of our PCA-based
including the training and test steps. The training flow follows               novelty detector by increasing the separation between normal
threemainsteps:(i)traintheCFE,(ii)encodeNc intofeatures,                       and anomalous data points in feature space. To achieve this,
and  (iii)  train  PCA-based  novelty  detector  on  the  encoded              we leverage the clean normal data Nc  (which is also used
Nc data. Each of these steps is performed at every training                    to train the PCA model). Using K-Means clustering [25], we
experience. For step (i), the CFE is trained on Xtrain using                   identify which points in Xtrain are most similar to Nc and
the loss function from Equation 1. For step (ii), the subset                   then  push  these  points  apart  in  feature  space.  Specifically,
of  normal  data Nc  is  encoded  by  passing  it  through  the                LCS  leverages  K-Means  clustering  to  assign  pseudo-labels
trained CFE, where we encode the entire set. Ultimately, in                    to all points in Xtrain. Then it utilizes triplet margin loss
step  (iii),  we  fit  the  PCA  novelty  detection  model  to  this           [26] to maximize the Euclidean distance between the different
encoded normal data. This completes the CND-IDS training,                      pseudo labels. Calculating theLCS pseudo-labels involves the
and  we  then  proceed  to  evaluate  on  the  test  experiences.              following steps: 1) Fit K-Means clustering to all points in
```


### PDF page 4

[View original page, figures and tables](assets/page-004.png)

```text
Xtrain; 2) Find the cluster labels of all Nc  data points; 3)                                   IV.  EXPERIMENTAL ANALYSIS
            Create the set of ”normal data” clusters CLN, where each                      A. Experimental Setup
            clustercontainsatleastonepointfromNc;4)Assignclass0to                            Datasets:  Table  I  provides  a  detailed  breakdown  of  the
            pointsinXtrain iftheirassociatedclusterisinCLN,andclass                       SOTA intrusion datasets utilized in our study. For IIoT in-
            1 otherwise. In summary, after fitting K-Means toXtrain, we                   trusion, we use IIoT datasets X-IIoTID [28] and WUSTL-
            identify the clusters associated with Nc. If a cluster contains               IIoT [29]. We also include commonly used network intrusion
            any point from Nc, all points in that cluster are assigned to                 datasets  CICIDS2017  [30]  and  UNSW-NB15  [31].  For  X-
            class 0; otherwise, they are assigned to class 1. This effectively            IIoTID [28], CICIDS2017 [30], and UNSW-NB15 [31], we
            splits  the  data  into  two,  where  0  would  represent  normal             split the data across five experiences such that each experience
            pseudo-label, and 1 would represent anomalous pseudo-label                    contains two to four attacks. For WUSTL-IIoT [29], we split
               After assigning the pseudo-labels, the final loss is computed              the data across four experiences such that each experience
            using the widely adopted triplet margin loss [26], defined as:                contains one attack. We perform this data split to simulate an
                             LCS = max(∆ap−∆an+m,0)                  (2)                  evolving data stream with emerging cyber attacks over time
            where  ∆ap  represents  the  Euclidean  distance  between  an                 where each experience contains different attacks.
            anchor point and a positive point (a point of the same class),                               TABLE I: Selected Intrusion Datasets
            and ∆an is the Euclidean distance between the anchor and a
            negative point (a point from a different class). The termm> 0
            is a hyper-parameter that specifies the desired margin between
            positive and negative points.
               Reconstruction Loss: The reconstruction loss ensures that
            the features embedded by the encoder retain significant infor-                   Baselines: We evaluate our algorithm against two SOTA
            mation from the original data. We found that this approach                    unsupervised continual learning (UCL) algorithms: the Au-
            helps the PCA extractor better generalize to future and past                  tonomous  Deep  Clustering  Network  (ADCN)  [27],  and  an
            experiences by forcing the model to learn encodings that align                autoencoder paired with K-Means clustering. The autoencoder
            more closely with the original data. The reconstruction loss is               K-Means model is combined with Learning without Forgetting
            the mean squared error (MSE) between the original input and                   [32] continual learning loss; we refer to this model as LwF.
            the reconstructed output of the decoder. Let h be the encoded                 Note that both ADCN and LwF require a small amount of
            feature of point x. Then LR =MSE(decoder(h),x).                               labeled normal and attack data to perform classification. We
               Continual  Learning  Loss:  Our  solution  to  catastrophic                also compare our approach against SOTA ND methods: local
            forgetting  is  employing  a  latent-based  regularization  loss,             outlier factor (LOF) [15], one-class support vector machine
            LCL  [27]. This loss ensures that as the model learns new                     (OC-SVM) [15], principal component analysis (PCA) [23],
            information, it retains knowledge from past experiences. LCL                  and Deep Isolation Forest (DIF) [33]. Since these ND models
            can  be  formulated  as: LCL  =Pci<cMSE(hc,hi)  where                         cannot be retrained on unlabeled contaminated data, continual
            c represents the current experience, and hj  is the encoded                   learning is not feasible for these methods.
            embedding of input x at experience j. The loss is computed                       Evaluation Metrics: To evaluate the model performance,
            by summing the MSE between the current embedding (hc) and                     we report F1 score. Since there is a class imbalance within
            all previous embeddings hi where i<c. This ensures that the                   these datasets, to simulate real world IDS, F1 score gives an
            current embedding is still similar to the previous embedding,                 accurate idea on attack detection. For the continual learning
            thereby preventing catastrophic forgetting. To calculate past                 methods, we evaluate their performance at the end of each
            embedding,wepassthecurrentdatapointxintoapastversion                          training experience on all experience test sets. This generates a
            of the model. This requires the model to save its state between               matrixofF1 scoreresultsRij suchthatiisthecurrenttraining
            experiences but does not require it to save any data, which can               experience, and j is the testing experience. To summarize this
            significantly reduce storage overhead.                                        matrix of results, we report widely used CL metrics [34]: av-
            D. PCA-based Novelty Detection                                                erage F1 score on current experience (AVG), forward transfer
                                                                                          (FwdTrans), and backward transfer (BwdTrans). For a matrix
               Inspired by [23], we create a PCA-based novelty detection                  Rij  with m  total  experiences,  our  metrics  are  formulatedPP
            approach. Let h denote the output feature from our feature                    as  follows:  AVGF1  =           i=jRij                           j>iRij
            extractor.  We  utilize  principal  component  analysis  transfor-                                Pm            m     ;  FwdTransF1  =        m∗(m−1)2      ;
            mation T to map the input feature from a high dimensional                     BwdTransF1 =          i  Rmi−Riim∗(m−1)

                                                                                                                     2         . AVG is the average performance
            space to low dimensional space T : h → l. We then utilize                     on  the  current  test  experience  at  every  point  of  training.
            the feature reconstruction error (FRE) as the anomaly score:                  FwdTrans is the average performance on “future” experiences,
            FRE  =h−T−1(l)2,  where  T−1  is  the  inverse  PCA                       which  simulates  performance  on  zero-day  attacks.  Finally,
            transform. The anomaly score is therefore the reconstruction                  BwdTrans  is  the  average  change  in  performance  of  “past”
            loss from this method. We train the PCA transformation on                     test experiences at a “future” point of training. A negative
            the subset of normal data Nc after it is encoded by the CFE.                  BwdTrans indicates catastrophic forgetting, whereas a positive







    Dataset          Size     Normal Data    Attack Data  Attack Types
 X-IIoTID [28]      820,502      421,417       399,417         18
WUSTL-IIoT [29]    1,194,464    1,107,448      87,016           4
CICIDS2017 [30]    2,830,743    2,273,097      557,646         15
UNSW-NB15 [31]      257,673      164,673       93,000          10
```


### PDF page 5

[View original page, figures and tables](assets/page-005.png)

```text
Fig. 3: Continual learning metric results of ADCN [27], LwF [32], and CND-IDS


BwdTrans indicates the model actually improved performance                     TABLE II: CND-IDS Improvement over UCL Baselines
on past experiences after learning a future experience. Overall,                         Baseline        Dataset        AVG      FwdTrans
AVG  measures  seen  attacks,  FwdTrans  measures  zero-day                            ADCN [27]        X-IIoTID       2.02×       5.00×
attacks, and BwdTrans measures forgetting. For all metrics,                                           WUSTL-IIoT       4.50×      6.47×
                                                                                                      CICIDS2017       1.37×       1.73×
a higher positive result indicates a better performance.                                              UNSW-NB15        1.29×       1.44×
  We also report the threshold-free metric Precision-Recall                             LwF [32]        X-IIoTID       1.46×       1.35×
Area Under the Curve (PR-AUC) [35]. Since CND-IDS re-                                                 WUSTL-IIoT       6.11×      3.47×
quires  selecting  a  threshold,  PR-AUC  allows  us  to  assess                                      CICIDS2017       1.93×       2.64×
                                                                                                      UNSW-NB15        1.11×       1.02×
model performance independently of the threshold. We choose
PR-AUC over Receiver Operating Characteristic Area Under
the Curve (ROC-AUC) because ROC-AUC can give mislead-                       proportional increase over the baseline performance. We do
ingly high results in the presence of class imbalance [35].                 notincludeBwdTransbecauseaproportionalincreasedoesnot
  Hyperparameters: We utilize elbow method [36] for deter-                  make sense for a metric that can be negative. CND-IDS has
mining the number of clusters K. We set λR and λCL to 0.1,                  up to4.50× and6.1× AVG improvement on ADCN and LwF,
and for m we use 2 after careful experimentation. For the AE                respectively.Inaddition,CND-IDShasupto6.47×and3.47×
modules of CND-IDS, we use 4-layer MLP with 256 neurons                     FwdTrans improvement on ADCN and LwF. Averaged across
in the hidden layers. We train it using Adam optimizer [37]                 alldatasets,CND-IDSshowsa1.88×and1.78×improvement
with a learning rate of 0.001. For PCA, we use the explained                on AVG, and a 2.63× and 1.60× improvement on FwdTrans,
variance method and set it to 95% [23].                                     compared to ADCN and LwF, respectively.
  Hardware: We run our experiments on NVIDIA GeForce                           Overall, these results highlight the benefit of continual ND
RTX 3090 GPU, with a AMD EPYC 7343 16-Core processor.                       over UCL methods for IDS. CND-IDS, with its PCA-based
B. Results                                                                  novelty detector, excels by effectively harnessing the normal
                                                                            data to identify attacks. A key strength of our approach lies
  Continual  Learning  Comparison:  Fig.  3  presents  the                  in  the  assumption  that  normal  data  forms  a  distinct  class,
results of our approach CND-IDS compared with ADCN [27]                     while everything else is treated as anomalous. This assumption
and LwF [32]. CND-IDS shows the best performance on both                    is particularly well-suited to IDS. In contrast, methods like
seen (AVG) and unseen (FwdTrans) attacks across all datasets.               ADCN  and  LwF  do  not  make  this  distinction  where  they
CND-IDS also has the highest BwdTrans on all except one                     handle both normal and attack data similarly, limiting their
dataset (UNSW-NB15). The average BwdTrans of CND-IDS                        ability to fully exploit the inherent structure of the data.
(0.87%) is higher than the average BwdTrans of both ADCN                       Novelty  Detectors  Comparison:  Fig.  4  compares  LOF
(-0.06%) and LwF (0.09%). Notably, the BwdTrans of CND-                     [15], OC-SVM [15], PCA [23], and DIF [33] with CND-IDS
IDS is positive for three datasets. Indicating past experiences             on all datasets. The average F1 score of the novelty detection
actually improve after training on future experiences for these             methods are compared to the AVG of CND-IDS. It can be seen
datasets. Given the high FwdTrans as well, our approach finds               CND-IDS outperforms all other methods across all datasets.
features that generalize well to future experiences.                        The  two  best  performing  methods  are  DIF  and  PCA.  The
  Table  II  shows  the  improvement  of  CND-IDS  over  the                averageF1 score improvement across all datasets of CND-IDS
UCL  baselines  on  all  datasets.  Bold  and  underlined  cases            is1.16× and1.08× over DIF and PCA, respectively. These re-
indicate  the  best  and  the  second  best  improvements  with             sults highlight the critical role of leveraging information from
respect to each metric, respectively. These improvements were               unsupervised data streams. Unlike these ND algorithms, CND-
calculated  by  comparing  the  performance  of  CND-IDS  to                IDSiscapableofcontinuouslylearningfromthisunsupervised
the  baselines,  where  the  improvement  values  represent  the            data, enabling it to enhance PCA reconstruction over time. By
```


### PDF page 6

[View original page, figures and tables](assets/page-006.png)

```text
TABLE III: Ablation Study of CND-IDS Loss Functions

                                                                                                       Strategy               AVG       BwdTrans     FwdTrans
                                                                                                      CND-IDS                76.92%       0.87%       73.70%
                                                                                                CND-IDS (w/o LCS)            66.23%       0.09%       70.26%
                                                                                                 CND-IDS (w/o LR)            72.86%      -5.44%       67.82%
                                                                                            CND-IDS (w/o LR and LCL)         79.92%      -11.26%      71.01%

                                                                                         TABLE IV: Average inference time (in ms) per test sample



           Fig. 4: Average F1 score on all experiences of CND-IDS and
               novelty detection methods: LOF, OC-SVM, PCA, DIF                         future.  This  would  make  sense  as  a  regularization  loss  to
                                                                                        improve  continual  learning  would  slightly  decrease  perfor-
                                                                                        mance in non-continual scenario. Overall CND-IDS has the
                                                                                        best results when taking every metric category into account.
                                                                                        Notably the low BwdTrans and FwdTrans of CND-IDS (w/o
                                                                                        LR) showcases how the reconstruction loss helps CND-IDS
                                                                                        generalize better to unseen and past data. This highlights the
                                                                                        power of LR to provide good features for continual learning.
                                                                                        D. Overhead Analysis
                                                                                           Table  IV  evaluates  the  inference  overhead  of  CND-IDS
                  Fig. 5: Thresholding Free Evaluation of CND-IDS                       compared to ADCN [27], LwF [32], DIF [33], and PCA [23].
                                                                                        CND-IDS offers the fastest inference time among continual
                                                                                        learning methods. Out of novelty detection methods, CND-
           integratingevolvingdatapatterns,CND-IDSnotonlyadaptsto                       IDS is second only to PCA. We attribute the efficiency of
           newanomaliesbutalsoimprovesitsoveralldetectionaccuracy,                      CND-IDS  to  avoiding  the  clustering  classification  used  by
           demonstrating a clear advantage in dynamic environments.                     LwF  and  ADCN.  The  difference  between  CND-IDS  and
              Pre-threshold Evaluation: While thresholding plays a cru-                 PCA  is  minimal,  only  0.0001  milliseconds  slower,  due  to
           cial role in attack decision-making, evaluating model predic-                the  additional  but  lightweight  step  of  encoding  the  data.
           tion performance before applying threshold is also important.                Considering  that  the  average  median  flow  duration  across
           TheUCLalgorithms(ADCN[27]andLwF[32])donotoutput                              datasets  is  27.77  milliseconds,  the  overhead  introduced  by
           anomalyscoresbecausetheyselectclassesbasedontheclosest                       CND-IDS is negligible in the context of real-time traffic flow.
           labeled cluster. Therefore we compare against the two best                                              V.  CONCLUSION
           ND methods: DIF [33] and PCA [23]. Fig. 5 presents the                          IDS are essential for ensuring a robust and comprehensive
           PR-AUC values of DIF, PCA, and CND-IDS. It can be seen                       security strategy. ML methods have been recently adopted for
           that CND-IDS provides the best threshold free results, which                 this task due to their great prediction performance. However,
           aligns with the threshold-based results presented earlier. The               current ML-IDS solutions are vulnerable to under-represented
           strong performance of CND-IDS in both pre-threshold and                      attacks and constantly changing environments. Therefore, fu-
           threshold-based  evaluations  demonstrates  that  the  model  is             ture  IDS  must  be  able  to  (i)  generalize  to  unseen  attacks
           robust regardless of the decision threshold.                                 and  (ii)  adapt  to  evolving  attacks  over  time.  To  address
           C. Ablation Study                                                            these challenges, we present CND-IDS, a continual novelty
              To demonstrate the impact of our loss function components,                detection  based  IDS  algorithm.  CND-IDS  combines  PCA
           we perform an ablation study. Table III shows the results of                 novelty  detection  with  a  continual  feature  extractor.  CND-
           CND-IDS  with  each  loss  function  removed  to  demonstrate                IDS is capable of continually learning with no attack labels,
           their individual effectiveness. Bold and underlined cases in-                allowing it to detect attacks in a changing data stream. We
           dicate the best and the second best performances with respect                have demonstrated that on realistic intrusion datasets, CND-
           to each metric, respectively. CND-IDS without reconstruction                 IDS is up to 6.1× more effective than SOTA unsupervised
           loss (LR) and CND-IDS without cluster separation loss (LCS)                  CL method for detecting seen attacks and up to 6.5× more
           performs worse in all categories. CND-IDS without both LR                    effective at detecting future attacks.
           and  continual  learning  loss  (LCL)  actually  performs  better                                    ACKNOWLEDGMENTS
           AVG  but  has  worse  BwdTrans  and  FwdTrans.  AVG  does                       ThisworkhasbeenfundedinpartbyNSF,withawardnum-
           not account for past experiences, so the significantly negative              bers #1826967, #1911095, #2003279, #2052809, #2100237,
           BwdTrans indicates CND-IDS w/o LR and LCL forgets, and                       #2112167, #2112665, and in part by PRISM and CoCoSys,
           therefore would perform worse on those experiences in the                    centers in JUMP 2.0, an SRC program sponsored by DARPA.








     Strategy         CND-IDS     ADCN       LwF       DIF      PCA
Inference Time (ms)    0.0019     0.4061    0.0677   1.0535    0.0018
```


### PDF page 7

[View original page, figures and tables](assets/page-007.png)

```text
REFERENCES                                                            ACM SIGKDD international conference on knowledge discovery & data
                                                                                                          mining, pp. 2828–2837, 2019.
 [1]I. Kumar, “Emerging threats in cybersecurity: A review article,”     Inter-                    [25]D. Seo, S. Kim, S. Oh, and S.-H. Kim, “K-means clustering-based safety
      national Journal of Applied and Natural Sciences, vol. 1, p. 01–08, Jul.                            system  in  large-scale  industrial  site  using  industrial  wireless  sensor
      2023.                                                                                               networks,” Sensors, vol. 22, no. 8, 2022.
 [2]H.-J. Liao     et al., “Intrusion detection system: A comprehensive review,”                   [26]F. Schroff       et al., “Facenet: A unified embedding for face recognition and
      Journal of Network and Computer Applications, vol. 36, no. 1, pp. 16–                               clustering,” in Proceedings of the IEEE conference on computer vision
      24, 2013.                                                                                           and pattern recognition, pp. 815–823, 2015.
 [3]O. Gungor, T. Rosing, and B. Aksanli, “Roldef: Robust layered defense                          [27]A.  Ashfahani  and  M.  Pratama,  “Unsupervised  continual  learning  in
      for  intrusion  detection  against  adversarial  attacks,”  in 2024  Design,                        streaming environments,” IEEE Transactions on Neural Networks and
      Automation & Test in Europe Conference & Exhibition (DATE), pp. 1–6,                                Learning Systems, vol. 34, no. 12, pp. 9992–10003, 2023.
      IEEE, 2024.                                                                                  [28]M. Al-Hawawreh       et al., “X-iiotid: A connectivity-agnostic and device-
 [4]“Study: Hackers attack every 39 seconds.” https://eng.umd.edu/news/                                   agnosticintrusiondatasetforindustrialinternetofthings,”IEEEInternet
      story/study-hackers-attack-every-39-seconds. Accessed: 2023-01-11.                                  of Things Journal, vol. 9, no. 5, pp. 3962–3977, 2021.
 [5]E.  Verwimp      et  al.,  “Continual  learning:  Applications  and  the  road                 [29]M.  Zolanvari        et  al.,  “Wustl-iiot-2021  dataset  for  iiot  cybersecurity
      forward,” arXiv preprint arXiv:2311.11908, 2023.                                                    research.” Washington University in St. Louis, USA, oct 2021.   http:
 [6]L. Wang, X. Zhang, H. Su, and J. Zhu, “A comprehensive survey of                                      //www.cse.wustl.edu/∼jain/iiot2/index.html.
      continual learning: theory, method and application,” IEEE Transactions                       [30]I.  Sharafaldin        et  al.,  “Toward  generating  a  new  intrusion  detection
      on Pattern Analysis and Machine Intelligence, 2024.                                                 dataset and intrusion traffic characterization,” in International Confer-
 [7]R. Kozik      et al., “Balanced efficient lifelong learning (b-ella) for cyber                        ence on Information Systems Security and Privacy, 2018.
      attack detection.,” J. Univers. Comput. Sci., vol. 25, no. 1, pp. 2–15,                      [31]N. Moustafa and J. Slay, “Unsw-nb15: a comprehensive data set for
      2019.                                                                                               network intrusion detection systems (unsw-nb15 network data set),” in
 [8]R. R. Karn, P. Kudva, and I. M. Elfadel, “Learning without forgetting:                                Military  Communications  and  Information  Systems  Conference  (Mil-
      A new framework for network cyber security threat detection,” IEEE                                  CIS), pp. 1–6, IEEE, 2015.
      Access, vol. 9, pp. 137042–137062, 2021.                                                     [32]Z. Li and D. Hoiem, “Learning without forgetting,”       IEEE Transactions
 [9]S. Prasath      et al., “Analysis of continual learning models for intrusion                          on Pattern Analysis and Machine Intelligence, vol. 40, no. 12, pp. 2935–
      detection system,” IEEE Access, vol. 10, pp. 121444–121464, 2022.                                   2947, 2018.
[10]S.  kumar  Amalapuram,  S.  S.  Channappayya,  and  B.  Tamma,  “Aug-                          [33]H.  Xu,  G.  Pang,  Y.  Wang,  and  Y.  Wang,  “Deep  isolation  forest
      mented memory replay-based continual learning approaches for network                                for anomaly detection,” IEEE Transactions on Knowledge and Data
      intrusiondetection,”inThirty-seventhConferenceonNeuralInformation                                   Engineering, pp. 1–14, 2023.
      Processing Systems, 2023.                                                                    [34]N. D      ´ıaz-Rodr´ıguez, V. Lomonaco, D. Filliat, and D. Maltoni, “Don’t
[11]C. Oikonomou       et al., “A multi-class intrusion detection system based on                         forget, there is more than forgetting: new metrics for continual learning,”
      continual learning,” in 2023 IEEE International Conference on Cyber                                 arXiv preprint arXiv:1810.13166, 2018.
      Security and Resilience (CSR), pp. 86–91, IEEE, 2023.                                        [35]J. Davis and M. Goadrich, “The relationship between precision-recall
[12]S. Channappayya, B. R. Tamma,        et al., “Augmented memory replay-                                and roc curves,” in Proceedings of the 23rd International Conference
      based continual learning approaches for network intrusion detection,”                               on Machine Learning, ICML ’06, (New York, NY, USA), p. 233–240,
      Advances in Neural Information Processing Systems, vol. 36, 2024.                                   Association for Computing Machinery, 2006.
[13]M.  Macas,  C.  Wu,  and  W.  Fuertes,  “A  survey  on  deep  learning                         [36]J. Han, M. Kamber, and J. Pei,       Data Mining: Concepts and Techniques.
      for cybersecurity: Progress, challenges, and opportunities,” Computer                               Elsevier, 2011.
      Networks, vol. 212, p. 109032, 2022.                                                         [37]D. P. Kingma and J. Ba, “Adam: A method for stochastic optimization,”
                                                                                                          2017.
[14]M. Verkerken, L. D’hooge, T. Wauters, B. Volckaert, and F. De Turck,
      “Towards  model  generalization  for  intrusion  detection:  Unsupervised
      machine learning techniques,” Journal of Network and Systems Man-
      agement, vol. 30, pp. 1–25, 2022.
[15]K.  Faber,  R.  Corizzo,  B.  Sniezynski,  and  N.  Japkowicz,  “Lifelong
      continual learning for anomaly detection: New challenges, perspectives,
      and insights,” IEEE Access, vol. 12, p. 41364–41380, 2024.
[16]N. Gupta, V. Jindal, and P. Bedi, “A survey on intrusion detection and
      prevention systems,” SN Comput. Sci., June 2023.
[17]O. Gungor, E. Li, Z. Shang, Y. Guo, J. Chen, J. Davis, and T. Rosing,
      “Rigorous  evaluation  of  machine  learning-based  intrusion  detection
      against adversarial attacks,” in 2024 IEEE International Conference on
      Cyber Security and Resilience (CSR), pp. 152–158, IEEE, 2024.
[18]H. Liu and B. Lang, “Machine learning and deep learning methods for
      intrusion detection systems: A survey,” applied sciences, vol. 9, no. 20,
      p. 4396, 2019.
[19]P. Ruvolo and E. Eaton, “Ella: An efficient lifelong learning algorithm,”
      in International conference on machine learning, pp. 507–515, PMLR,
      2013.
[20]S.  K.  Amalapuram         et  al.,  “Continual  learning  for  anomaly  based
      network  intrusion  detection,”  in 2022  14th  International  Conference
      on COMmunication Systems & NETworkS (COMSNETS), pp. 497–505,
      IEEE, 2022.
[21]G. Kim, C. Xiao, T. Konishi, Z. Ke, and B. Liu, “Open-world continual
      learning: Unifying novelty detection and continual learning,” 2023.
[22]R.Aljundi,D.O.Reino,N.Chumerin,andR.E.Turner,“Continualnov-
      elty detection,” in Conference on Lifelong Learning Agents, pp. 1004–
      1025, PMLR, 2022.
[23]A. Rios, N. Ahuja, I. Ndiour, U. Genc, L. Itti, and O. Tickoo, “incdfm:
      Incremental deep feature modeling for continual novelty detection,” in
      European Conference on Computer Vision, pp. 588–604, Springer, 2022.
[24]Y. Su        et al., “Robust anomaly detection for multivariate time series
      through stochastic recurrent neural network,” inProceedings of the 25th
```
