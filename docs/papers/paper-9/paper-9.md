# Continual Learning for Intrusion Detection Under Evolving Network Threats

**Authors:** Chaoqun Guo; Xihan Li; Jubao Cheng; Shunjie Yang; Huiquan Gong

**Publication:** Future Internet (2025).

**Publication DOI:** https://doi.org/10.3390/fi17100456

**Verified free PDF:** https://mdpi-res.com/d_attachment/futureinternet/futureinternet-17-00456/article_deploy/futureinternet-17-00456.pdf

**Downloaded version:** Publisher version of record, open access, Creative Commons Attribution.

**Qualification:** Q2, COMPUTER SCIENCE, INFORMATION SYSTEMS. Journal rankings use the 2024 JIF category quartile (June 2025 JCR), not an asserted 2026 ranking.

**Integrity:** 25 pages; 682,136 bytes; SHA-256 `f40294fa0fb944c27408aea0537caa2051fea7397ce936dc0a43dd79de8d4e03`. Verified 8 October 2026.

## Reading and extraction note

The PDF is the authoritative complete manuscript. Below is automatic page-level text extraction, not a newly authored summary or a verbatim-quality transcription. Two-column order, formulas, ligatures and table spacing can be imperfect. Every page has a rendered PNG in `assets/` for inspecting figures, equations and tables at their original locations. Publication metadata is saved alongside the images. The technical review is in [the selection audit](../phase2-selection-audit.md).

## Full manuscript text


### PDF page 1

[View original page, figures and tables](assets/page-001.png)

```text
Article
Continual Learning for Intrusion Detection Under Evolving
Network Threats

Chaoqun Guo †          , Xihan Li †     , Jubao Cheng         , Shunjie Yang         and Huiquan Gong *



                                     School of Software Engineering, Beijing Jiaotong University, Beijing 100044, China; chqguo@bjtu.edu.cn (C.G.);
                                     xihan26@bjtu.edu.cn (X.L.); chengjubao@bjtu.edu.cn (J.C.); shunjie@bjtu.edu.cn (S.Y.)
                                     *   Correspondence: hqgong@bjtu.edu.cn; Tel.: +86-010-5168-3768
                                     †  These authors contributed equally to this work.


                                     Abstract

                                     Intheface ofever-evolvingcyberthreats,modern intrusiondetectionsystems(IDS)must
                                     achievelong-term adaptability without sacrificing performanceon previously encountered
                                     attacks. Traditional IDS approaches often rely on static training assumptions, making them
                                     pronetoforgettingoldpatterns,underperforminginlabel-scarceconditions,andstruggling
                                     withimbalancedclassdistributionsasnewattacksemerge. Toovercometheselimitations,
                                     wepresentacontinuallearningframeworktailoredforadaptiveintrusiondetection. Unlike
                                     priormethods,ourapproachisdesignedtooperateunderreal-worldnetworkconditions
                                     characterizedbyhigh-dimensional,sparsetrafficdataandtask-agnosticlearningsequences.
                                     The framework combines three core components: a clustering-based memory strategy that
                                     selectivelyretainsinformativehistoricalsamplesusingDP-Means;multi-levelknowledge
                                     distillationthatalignscurrentandpreviousmodelstatesatoutputandintermediatefeature
                                     levels; and a meta-learning-driven class reweighting mechanism that dynamically adjusts
                                     to shifting attack distributions. Empirical evaluations on benchmark intrusion detection
                                     datasets demonstratethe framework’s ability to maintainhigh detection accuracywhile
                                     effectively mitigating forgetting. Notably, it delivers reliable performance in continually
                                     changing environments where the availability of labeled data is limited, making it well-
                                     suited for real-world cybersecurity systems.

                                     Keywords:intrusiondetection;continuallearning;semi-supervisedlearning;classimbalance;
AcademicEditor: CarloBlundo          knowledgedistillation;meta-learning

Received: 14August2025
Revised: 1October2025
Accepted: 2October2025
Published: 4October2025              1. Introduction

Citation:   Guo,C.;Li,X.;Cheng,J.;         Inopenandcontinuouslyevolvingnetworkenvironments,intrusionbehaviorsdemon-
Yang,S.;Gong,H.ContinualLearning     stratedistinctivecharacteristicssuchascontinuousemergence,diverseattackmodalities,
forIntrusionDetectionUnder
EvolvingNetworkThreats. Future       and sparse distributionpatterns. As adversaries refinetheir techniques, IDS must not only

Internet2025,17,456.https://doi.org/ swiftly recognize known threats but also adapt in real-time to detect novel and evolving
10.3390/fi17100456                   attack types. However, traditional static modeling approaches, which rely on fixed task

Copyright: ©2025bytheauthors.        settingsandfullylabeled datasets,areill-suitedfordynamicdeploymentscenariosdue to
LicenseeMDPI,Basel,Switzerland.      the following three core limitations:

Thisarticleisanopenaccessarticle     •      Catastrophicforgetting. Conventionalmodelsoftensufferfromcatastrophicforgetting,
distributedunderthetermsand                where learning new tasks leads to the degradation of performance on previously
conditionsoftheCreativeCommons
Attribution(CCBY)license                   learnedtasks. Thisisparticularlyproblematicinintrusiondetection,wherethesystem

(https://creativecommons.org/              must retain knowledge of both historical and emerging threats.

licenses/by/4.0/).



Future Internet2025,17, 456                                                                                                                                                      https://doi.org/10.3390/fi17100456
```


### PDF page 2

[View original page, figures and tables](assets/page-002.png)

```text
Future Internet2025,17, 456                                                                                                           2 of 25



                                   •      Labelscarcity. Inreal-worldscenariossuchasindustrialcontrolsystemsandInternet
                                        of Things (IoT) infrastructures, most traffic data are collected in raw form without
                                        labels. Thehighcostandtimerequirementsofmanualannotationrenderonlyasmall
                                        portion of these data usable for supervised learning, leaving vastamounts of valuable
                                        unlabeled traffic underutilized and limiting the system’s capacity to capture latent
                                        attack behaviors.
                                   •      Class imbalance and distributionbias. During model learning, new classes typically
                                        dominatethetrainingstreamintermsofvolumeandfrequency. Thisimbalancebiases
                                        the model towards recent classes, leading to the erosion of performance on earlier,
                                        potentiallycriticalcategories—aparticularlysevereproblemforthedetectionofrare
                                        but impactful attacks.
                                        Tomitigatethesechallenges,recentstudieshavebeguntoexploretheintegrationof
                                   ContinualLearning(CL)[1,2]andSemi-SupervisedLearning(SSL)[3,4]inthedomainofin-
                                   trusion detection. CL aims to maintain long-term knowledge retention through techniques
                                   suchasmemoryreplay,knowledgedistillation,andregularization-basedconstraints. SSL,
                                   on the other hand, enhances the exploitation of unlabeled data through pseudo-labeling,
                                   consistency training, and contrastive learning, thereby improving generalization under
                                   limited supervision.
                                        Despitetheirpromise,mostexistingCLandSSLmethodsaredevelopedinthecontext
                                   of computer vision or few-shot classification and are not readily applicable to the unique
                                   propertiesofnetworktraffic,includinghigh-dimensionalfeaturespaces, inter-classsimi-
                                   larity, and evolving data distributions. Furthermore, real-world deployment issues such
                                   asblurredtaskboundaries,non-stationarylabelgrowth,andlowoverlapbetweenclasses
                                   arefrequentlyoverlooked,leadingtoperformancedegradationwhenthesemethodsare
                                   directly transferred to the IDS domain.
                                        To address these limitations, we propose a dynamic intrusion detection framework
                                   that integrates SSL with CL through three key mechanisms. Our main contributions are
                                   as follows:
                                   •      Dynamic memoryconstructionfor discriminativeknowledge retention. Wedesign a
                                        data-drivenmemoryselectionmechanismtailoredtothesparsityandhighdimension-
                                        ality of network traffic. By employing DP-Means clustering and uncertainty-based
                                        sampling, the model selectively retains both representative class centers and high-
                                        entropyboundary samples,enabling effectiveconsolidation ofpast knowledgewhile
                                        facilitating the learning of new attack patterns.
                                   •      Multi-level knowledge distillation for robust representation alignment. We propose
                                        ahierarchicalknowledgealignmentstrategythatdistillsknowledgeatthreelevels—
                                        outputlogits, attentionmaps, andfeaturerepresentations. This multi-faceted align-
                                        mentmitigates therisksof pseudo-labelnoiseand catastrophicforgetting, ensuring
                                        stable representation learning across task transitions.
                                   •      Meta-learning-based dynamic weighting for class imbalance mitigation. To address
                                        dynamic class distribution shifts and long-tailed data challenges, we incorporate a
                                        meta-learning-driven adaptive weighting mechanism. This component adjusts loss
                                        weights and biascorrections based onreal-time category frequency statistics, thereby
                                        enhancing model robustness against rare or under-represented attack types.
                                        Theseinnovationscollectivelyprovideascalableandgeneralizablesolutionforintru-
                                   siondetectionindynamic,label-scarce,andimbalancednetworkenvironments. Extensive
                                   experiments across multiple real-world datasets demonstrate that our framework consis-
                                   tentlyoutperformsstate-of-the-artmethodsintermsofcatastrophicforgettingsuppression,
                                   minority class recognition, and generalization under limited supervision, validating its
                                   practical deployment potential.
```


### PDF page 3

[View original page, figures and tables](assets/page-003.png)

```text
Future Internet2025,17, 456                                                                                                            3 of 25


                                   2. Related Work
                                   2.1. Continual Learning and Catastrophic Forgetting Mitigation
                                         CL empowersmodels to continuously acquirenew knowledge from sequentialdata
                                   streams without relying on full access to historical data [1,5]. This property is essential for
                                   IDS,whereattacksevolveovertimeandnovelthreats,suchasAdvancedPersistentThreats
                                   (APT)[6] andZero-Day Exploits[7] canemerge unpredictably. ExistingCL methodsare
                                   typically categorized into the four paradigms below [2].
                                         Regularization-Based: ApproachessuchasElasticWeightConsolidation(EWC)[8,9]
                                   andSynapticIntelligence(SI)[10]preventforgettingbypenalizingsignificantdeviations
                                   from previously importantparameters. These methodsembed knowledge retentioncon-
                                   straints directly into the optimization process.
                                         Replay-Based: TechniqueslikeiCaRL[11]andGDumb[12]maintainafixedmemory
                                   buffer of representative past samples for experience replay [13], enabling the model to
                                   revisit prior knowledge during training.  Recent extensions tailored to network traffic
                                   includemetric-basedmeta-learningforfew-shotclasses[14,15],andtheuseofconditional
                                   VAEs for generating polymorphic attack variants [16].
                                         Knowledge Distillation-Based:  Frameworks such as Learning without Forgetting
                                   (LwF) [17] employ output alignment via KL divergence between old and new model
                                   predictions. Extensions like PODNet [18] go further by enforcing feature-level structural
                                   consistency, preserving representational space continuity across tasks.
                                         Hybrid: Recent works [19,20] combine pseudo-labeling, consistency regularization,
                                   andknowledgedistillationtotacklenon-IIDunlabeleddatain CLsettings,offeringamore
                                   comprehensive adaptation strategy.
                                         While these methods have demonstrated success in domains like image classification,
                                   they encounter the following critical limitations when applied to intrusion detection:
                                   •      Highinter-classsimilarity: Networkattacksoftenexhibithighsimilarityacrossclasses,
                                         leading to confusion and reduced discriminative power. This is particularly problem-
                                         atic for replay-based methods that rely on distinct class boundaries.
                                   •      Sparse,high-dimensionalfeaturespaces: Networktrafficdataaretypicallysparseand
                                         high-dimensional, which complicates the replay efficiency of memory-based methods
                                         and exacerbates memory constraints.
                                   •      Rigid task-boundaryassumptions: Many existing CL frameworksassume clear task
                                         boundaries, which are often not present in real-world network environments.
                                         These limitations highlight the need for a class-agnostic,  sample-adaptive,  and
                                   representation-aligned CL strategy specifically designed for intrusion detection. An ef-
                                   fective solution must not only retain historical knowledgebut also dynamically adapt to
                                   non-stationary, imbalanced, and label-sparse traffic distributions—a gap that this work
                                   aims to fill.

                                   2.2. Semi-Supervised Learning in Intrusion Detection
                                         SSL has emerged as a powerful approach to address the label scarcity problem by
                                   leveraging large volumes of unlabeled data alongside limited labeled samples [21]. In the
                                   contextofintrusiondetection,thisisparticularlyvaluable. Networktrafficiscontinuously
                                   collected, but accurate annotation requires expert knowledge and labor-intensive proce-
                                   duressuchasbehavioralanalysisandattackforensics[4,22]. Thismakeslabeleddataboth
                                   scarce and costly, whereas unlabeled traffic is abundant but underutilized. In recent years,
                                   several SSL strategies have been applied tothe intrusion detection domain[23], including
                                   the ones below.
                                         Pseudo-LabelingApproaches: Methods suchasFixMatch [24]and Pseudo-Label[25]
                                   generate pseudo-labels for unlabeled data by selecting high-confidence predictions and
```


### PDF page 4

[View original page, figures and tables](assets/page-004.png)

```text
Future Internet2025,17, 456                                                                                                            4 of 25



                                   incorporatingthemintothesupervisedtrainingloss;whileeffectiveunderclass-balanced
                                   and well-separated distributions, these approaches are highly susceptible to pseudo-label
                                   noise, especially in the presence of novel or ambiguous attack types.
                                         ConsistencyRegularization: TechniqueslikeUDA[26]andMeanTeacher[27]apply
                                   perturbationstoinputsamplesandenforcepredictionconsistencyacrossaugmentedviews.
                                   These methods enhance model stability and robustness but rely heavily on the quality of
                                   dataaugmentation,whichcanbechallengingtodefineinhigh-dimensionalnetworktraffic.
                                         ContrastiveLearningandClustering-BasedMethods: RecentapproachessuchasMix-
                                   Match [28] and SimCLR [29] aim to learn robust semantic representations by encouraging
                                   clusteringinthefeaturespaceorcontrastingsimilar/dissimilarpairs. Thesestrategiesare
                                   well-suited for complex behavior modeling in intrusion detection, where attacks may form
                                   latent structures in the embedding space.
                                         Despite their promise, applying SSL to IDS presents the following domain-specific
                                   challenges:
                                   •      Pseudo-labelbiascausedbyclassimbalanceleadstotheoverfittingofmajorityclasses
                                         and neglect of rare but critical attacks.
                                   •      Extreme scarcity of novel attack samples in early task stages limits the availability of
                                         reliable pseudo-supervisory signals.
                                   •      Dynamicandnon-stationarydatadistributionsunderminethestabilityofSSLalgo-
                                         rithms, especially over long task sequences.
                                         ToeffectivelydeploySSLinpracticalIDS,itisimperativetoredesignpseudo-labeling
                                   strategies, regularization objectives, and sample selection mechanisms, particularly when
                                   integratingwithCLframeworks. Thisensuresstableandadaptivelearninginenvironments
                                   characterized by evolving threats, weak supervision, and severe class imbalance.

                                   2.3. Integration of Continual Learning and Semi-Supervised Learning
                                         The integration of CL and SSL has recently emerged as a promising direction for
                                   constructingadaptiveintrusiondetectionmodelsunderlow-labelanddynamicconditions.
                                   The overarching goal of such integration is to leverage the abundance of unlabeled data
                                   in evolving task sequences to enhance recognition of new or rare attack categories while
                                   preserving knowledge of previously encountered threats.
                                         However, combining CL and SSL is inherently non-trivial due to their conflicting
                                   optimization objectives.  CL emphasizes stability, i.e., retaining prior knowledge over
                                   time, whereas SSL prioritizes plasticity, i.e., rapidly adapting to new, unlabeled data.
                                   Achieving a robust balance between these competing goals requires addressing several
                                   fundamental challenges introduced below.
                                         Pseudo-label reliability under non-IID task streams. In practical settings, tasks are
                                   oftennon-independentandnon-identicallydistributed—witheachnewtaskintroducing
                                   distinct and potentially disjoint category distributions.  Naïve pseudo-labeling in such
                                   scenarios may introduce significant bias, leading to error accumulation and model drift,
                                   especially when rare or emerging attack types are involved.
                                         Loss of weight coordination between knowledge retention and knowledge acquisi-
                                   tion. SSL frameworks typically encourage aggressive incorporation of unlabeled data into
                                   the learning process. However, without proper weighting, this can distort the decision
                                   boundariesofpreviouslylearnedclasses,underminingCL’sobjectiveoflong-termmemory
                                   stability. Ajointoptimizationstrategyisrequiredtobalancetheinfluenceofsupervised,
                                   unsupervised, and replayed samples.
                                         Dynamic sample selection from unlabeled streams. Not all unlabeled samples are
                                   equallybeneficialfor learning. The challengeliesinidentifying andselectinginformative
                                   and reliable samples from a large, heterogeneous pool to be incorporated into the incre-
```


### PDF page 5

[View original page, figures and tables](assets/page-005.png)

```text
Future Internet2025,17, 456                                                                                                             5 of 25



                                   mentalupdate. Poorsampleselectioncanwaste computational resourcesor evendegrade
                                   model performance due to noise and redundancy.
                                         Several recentstudies havemade initialattempts tobridge these gaps. For example,
                                   Lechatet al. [30] proposed decoupling pseudo-label generation from incrementalupdates,
                                   whileCermellietal. [31]introducedverificationmodulestofilterlow-confidencepseudo-
                                   labels in the CL context. Nevertheless, these solutions are predominantly developed for
                                   image-based tasks and lack adaptation to the structural characteristics of network traffic,
                                   such as high feature dimensionality, inter-class similarity, and temporal evolution.
                                         These limitations underscore the need for domain-specific integration mechanisms
                                   that jointly optimize CL and SSL under the constraints of real-world intrusion detection.
                                   This paper addresses this gap by proposing a unified framework that tightly couples
                                   memory-efficient incremental updates with robust semi-supervised training strategies,
                                   specifically tailored for network traffic data.

                                   3. Methodology
                                         The proposed method aims to construct an intrusion detection framework with CL
                                   capabilities,enablingittoincrementallylearnnewattackcategorieswhileeffectivelyretain-
                                   ing knowledge of previously encountered threats. In addition, the framework is designed
                                   toleveragelarge-scaleunlabeledtrafficdatatoenhancemodelrobustnessunderlimitedsu-
                                   pervision. Tothisend,weproposeaunifiedapproach(seeFigure1)thatintegratesSSLwith
                                   CL,composedofthreekeymodules: adynamicmemoryselectionmoduleforcompactand
                                   discriminative historical sample retention; a multi-level knowledge alignment module to
                                   mitigate catastrophic forgetting across representational hierarchies; a meta-learning-based
                                   dynamic weighting module to address class imbalance and non-stationary distributions.






















                                   Figure 1. The proposed semi-supervised continual learning framework for intrusion detection.

                                   3.1. Problem Definition
                                         Define the intrusion detection process as a chronologically ordered sequence of in-
                                   cremental tasks: T  = {T0,T1,...T...,...,Tt−1,Tt}. Each task Tt introduces a new category
                                   subset Ct,where Ci∩Cj =∅ forany i̸= j. Thedatasetforeachtaskiscomposedofboth
                                   labeledandunlabeled samples: Dt = DLt ∪DUt ,where DLt =(xi,yi)nli=1 denotesthelabeled
                                   subset, and DUt  = (xj,·)nuj=1 represents the unlabeled samples. Typically, the number of
                                   unlabeled samples far exceeds the labeled ones (nu ≫ nl).  To mitigate forgetting, the
                                   modelmaintainsafixed-sizememorybufferMt−1,whichstoresrepresentativesamples
                                   from previous tasks. During training on task Tt, the objective is to learn a classifier fθt that
                                   satisfies the following criteria:
```


### PDF page 6

[View original page, figures and tables](assets/page-006.png)

```text
Future Internet2025,17, 456                                                                                                            6 of 25



                                   •      Accurate recognition of new classes:  for any x ∈  DLt , the model should predict
                                         fθt(x)= y, where y∈ Ct.
                                   •      Retention of historical knowledge: for all previously encountered labeled data x∈
                                         DLt−1, the model should maintain high accuracy on y∈St−1i=1 Ci.
                                   •      Utilization of unlabeled samples: the model should effectively extract discriminative
                                         representations from DUt  using unsupervised learning objectives to enhance general-
                                         ization and decision boundaries.
                                         Theoveralltrainingobjectiveattask Tt isformulatedasthejointminimizationoffour
                                   complementary loss components,

                                                          minθt  Lt =∑    λiLi,   Λ={sup,unsup,align,meta},                             (1)
                                                                     i∈Λ

                                   whereLx denotes the loss component associated with the respective task.

                                   3.2. Method Overview
                                         Thissectiondetailstheoverallarchitectureandkeymodulesoftheproposedframe-
                                   work, which integrates SSL and CL for robust, adaptive intrusion detection.

                                   3.2.1. Dynamic Memory Construction and Sample Selection Strategy
                                         AcentralchallengeinCLishowtoretainrepresentativehistoricalknowledgewithout
                                   storing excessive data. Traditional memory-basedapproaches suchas iCaRL[11] typically
                                   relyonfixed-ratiosampling,uniformselection,orclasscenterexemplars. Whileeffective
                                   insimpledomains,thesestrategiesareinsufficient for high-dimensionalandimbalanced
                                   network traffic, as they fail to preserve discriminative boundary information critical for
                                   distinguishing subtle attack patterns.
                                         Toovercomethislimitation,weintroduceahybridmemoryselectionmechanismthat
                                   combines online clustering viaDP-Means with uncertainty-aware sampling. Specifically,
                                   DP-Meansclusteringadaptivelypartitionsthefeaturespacewithoutrequiringapredefined
                                   number of clusters. It dynamically adjusts the number of modes based on data density,
                                   makingitsuitableforthe evolvingcategorystructures encounteredinreal-worldintrusion
                                   scenarios.  High-entropy sample selection is then employed to capture ambiguous or
                                   decision-critical points near boundaries, which are typically underrepresented by class
                                   centers. ThesetwocomponentsensurethatthememorybufferMt maintainsbothsemantic
                                   diversity and decision-boundary sensitivity.
                                         DP-MeansClustering: AsanonparametricalgorithmderivedfromtheinfiniteGaus-
                                   sianMixtureModel,DP-Meansautomaticallydeterminestheoptimalnumberofclusters K
                                   by minimizing the following objective:

                                                                                  K∑
                                                                  min{Ck}Kk=1              ∥xi−µk∥2+λK,                                         (2)
                                                                                 k=1 ∑xi∈Ck

                                   where Ck is the k-th cluster, µk denotes its centroid, and λ is a penalty coefficient that
                                   controls the trade-off between clustering tightness and the number of clusters. A largerλ
                                   encourages fewer, moregeneralized clusters, while a smallerλ allows for finergranularity
                                   to capture subtle variations in attack patterns. The algorithm iteratively assigns samples to
                                   the nearest centroid and updates centroids until convergence.
```


### PDF page 7

[View original page, figures and tables](assets/page-007.png)

```text
Future Internet2025,17, 456                                                                                                            7 of 25



                                         High-EntropySampleSelection: Toaugmentthememorywithsamplesthatimprove
                                   boundary representation, we select samples with high predictive uncertainty, measured
                                   by entropy.
                                                                                  C∑
                                                              H(p(y|x))=−            p(y= c|x)logp(y= c|x).                                   (3)
                                                                                c=1
                                         For each cluster,  samples are ranked by their entropy,  and the top-ke  samples
                                   are selected.
                                         SelectionProtocol: Underafixedmemorybudget M,weallocateaportionαMtocluster
                                   centers and(1−α)M to high-entropy samples. The final memory setMt is constructed by
                                   combining these two subsets.
                                         Complexity Analysis: The DP-Means algorithm has a time complexity of O(TnKd)
                                   pertask, where T isthe number ofiterations, n isthe numberofsamples, K isthe number
                                   of clusters, and d is the feature dimensionality.   The entropy calculation adds O(nC)
                                   complexity, where C is the number of classes. Sorting the entropies for ranking introduces
                                   anO(nlogn) factor. Overall, thememoryselection processremainsefficient andscalable
                                   for large datasets.
                                         The combined objective for memory construction is formulated to encapsulate
                                   both goals,
                                                                      K∑
                                                           Lmem =              ∥xi−µk∥2     +β· ∑       H(p(y|xj))   ,                              (4)
                                                                     k=1 ∑xi∈Ck                   xj∈H
                                                                     |         {z         }       |       {z        }
                                                                       Modal Preservation         Boundary Expression

                                   whereH isthesetofselectedhigh-entropysamples. Thefirsttermensuresclustercompact-
                                   ness and core semantic preservation, while the second term emphasizes uncertainty-aware
                                   boundary representation, with β as a balancing coefficient. This dual-objectivemechanism
                                   ensures the framework preserves both the core semantics and critical marginal information
                                   of past tasks, enhancing long-term stability and adaptive capacity. During this process,
                                   the influence of λ (in Equation (2)   ) is already indirectly reflected in the construction of
                                   the memory through the clustering structure it determines (K and µk).  A larger λ will
                                   producefewer,moregeneralizedclusters,resultinginfewercentralpointsinthememory;a
                                   smallerλ will produce more, finer clusters, resulting in more central pointsin the memory.
                                   Therefore,λ controlsthegranularityofthe“semanticdiversity”ofthememory,butititself
                                   does not need to appear in the final selection criteria.

                                   3.2.2. Multi-Level Knowledge Alignment Mechanism
                                         In dynamic intrusion detection, the model must continuously incorporate new attack
                                   patternswhilemaintainingaccuraterecognitionofpreviouslylearnedthreats. Traditional
                                   CLmethods,suchasLwF[17],implementoutput-leveldistillationbyaligningthelogitsof
                                   newandoldmodels. However, thissingle-layerknowledgeretentionstrategysuffersfrom
                                   several limitations: Shallow alignment at the output layer often leads to feature drift in
                                   intermediatelayers;themodel’sattentionfocusoncriticalfields(e.g.,specificports,time
                                   windows)mayshiftovertime;andinter-classrelationshipsintheembeddingspacemay
                                   become distorted bytask transitions, compromising the semantic structure of previously
                                   learned categories.
                                         To address these limitations, we propose a multi-level knowledge alignment mecha-
                                   nism that performs joint distillation across three hierarchical levels.
```


### PDF page 8

[View original page, figures and tables](assets/page-008.png)

```text
Future Internet2025,17, 456                                                                                                                8 of 25



                                          Logits-Level AlignmentModule: We firstalign the predicted class distributions ofthe
                                    currentmodel fnew andthefrozenhistoricalmodel fold byminimizingtheKullback–Leibler
                                    (KL) divergence between their softened outputs,

                                                                 Llogits = T2·KL       σ(zold/T)∥σ(znew/T)          ,                                     (5)

                                    where zold and znew arethelogitsfrom fold and fnew forthesameinput;σ(·) isthesoftmax
                                    function; and T is a temperature scaling parameter to smooth the output distribution.
                                    This term helpsstabilize class decision boundaries, particularlyin cases with overlapping
                                    categories (e.g., DoS vs. DDoS), where misalignment can severely impact performance.
                                          Attention-Level Alignment Module: To preserve the semantic focus of the model, we
                                    alignintermediateattentionmapsextractedfromcorrespondinglayersoftheoldandnew
                                    models. The Frobenius norm is used to minimize the discrepancy,

                                                                                      L∑
                                                                        Lattn = 1L       ∥A(l)old− A(l)new∥2F,                                                (6)
                                                                                     l=1

                                    where A(l) denotes the attention weight matrix at layer l; and L is the total number of
                                    aligned layers.  By maintaining consistent focus across tasks, this alignment enhances
                                    the model’s robustness and interpretability, especially in temporal or protocol-sensitive
                                    detection scenarios.
                                          Feature-LevelAlignmentModule: Topreservethegeometricandsemanticstructureof
                                    the learned representation space, we apply the BarlowTwins loss tothe high-level feature
                                    embeddings Zold and Znew. The loss function is defined as

                                                                         Lbt =∑(1−Cii)2+γ∑               C2ij,                                                (7)
                                                                                  i                  i̸=j

                                    whereC isthecross-correlationmatrixbetweennormalizedembeddingsofthetwomodels;
                                    Cii enforcesdiagonaldominance(invariance),and Cij suppressesoff-diagonalredundancy
                                    (decorrelation); and γ controls the regularization strength. This alignment helps retain
                                    clusterstructuresinthelatentspace(e.g.,ensuringDDoSandPortScanremainadjacentyet
                                    distinguishable), which is crucial for semantic consistency across tasks.
                                          The total alignment loss integrates the three components

                                                                  Lalign =∑      λiLi,   Λ={logits,attn,bt},                                      (8)
                                                                            i∈Λ

                                    where λi are tunable hyperparameters that balance the contribution of each term. This
                                    multi-levelalignmentstrategyensuresknowledgepreservationacrossthemodelhierarchy,
                                    alleviates representation degradation, and significantlyimproves continual generalization
                                    under evolving attack scenarios.

                                    3.2.3. Meta-Learning Driven Dynamic Weighting Mechanism
                                          In incremental intrusion detection, the model is exposed to a non-stationary data
                                    stream, where category distribution varies significantly across sequential tasks.  These
                                    variations manifest in several forms:  New class emergence:  previously unseen attack
                                    types are introduced at each stage; category frequency imbalance: rare or critical attacks
                                    appear only sporadically; andcategory overlap and drift: some classespersist across tasks,
                                    interfering with boundary preservation.
                                          Traditional CL methodsoften assume fixedclass priors andtherefore fail toadapt to
                                    such dynamic shifts. As a result, majority classes dominate the learning process, while
```


### PDF page 9

[View original page, figures and tables](assets/page-009.png)

```text
Future Internet2025,17, 456                                                                                                               9 of 25



                                    minorityclasses,especiallynewlyintroducedorrareattacktypes,areinsufficientlylearned.
                                    Thisimbalanceexacerbatescatastrophicforgettinganddegradesdetectionperformancein
                                    realistic settings,particularly under low-labelor few-shot scenarios. To address thisissue,
                                   we proposea meta-learning-drivendynamic weightingmechanism, which jointlylearns
                                    class-specificlossweightsandbiascorrectiontermsbasedonreal-timecategorystatistics.
                                    Thismoduleenablesadaptiverebalancingofmodeloptimizationtoimprovegeneralization
                                    on imbalanced, evolving attack distributions.
                                         LossWeightPredictionviaMeta-Learning: Let pc denotetheempiricalfrequencyof
                                    class c over the union of current task data and memory buffer


                                                                   pc = |{(xi,yi)∈ Dt∪Mt−1| yi = c}||Dt∪Mt−1|                  .                                        (9)

                                         Wethenpredicttheclass-specificlossweightwc usingalearnablefunction(modeled
                                    as a small MLP)

                                                                          wc = Softplus(MLP(pc)).                                                  (10)

                                         The Softplus activation ensures wc > 0 to prevent negative loss scaling. This allows
                                    the model to dynamically upweight underrepresented classes and downweight over-
                                    represented ones based on real-time distribution.  This design is inspired by long-tail
                                    classificationtechniques such asClass-Balanced Loss[32] andLDAM [33], butis extended
                                   with meta-learning to provide task-adaptive flexibility.
                                         BiasCorrectionintheLogitSpace: Tofurtherreduceclassbias,weintroducealogit-level
                                    adjustment term bc for each class c
                                                                                                     pc
                                                                      bc = b(t−1)c      +η·log  ∑k pk+ϵ      .                                           (11)

                                         Thisbiastermactsasapriorcorrection,counteractingclassfrequencydominanceby
                                    shiftingthe decision boundaryinfavor ofunderrepresented categories. Theupdatestep
                                    accumulates frequency information across tasks to maintain temporal smoothness.
                                         Combined Weighted Loss Formulation: The final objective combines both weighting and
                                    bias adjustment into a unified loss for both labeled and confidently pseudo-labeled data

                                                              Lmeta =−    ∑                wy·logp(y| x;θ+b),                                (12)
                                                                            (x,y)∈DLt∪DU∗t

                                   where DU∗t    is the subset of pseudo-labeled unlabeled data filtered by confidence thresh-
                                    olding; wy is thelearned importance weight forclass y; and b is theclass-wise bias vector
                                    appliedtologitsbeforesoftmax. Thisdynamiclossformulationallowsthemodeltofocus
                                    learning on critical and underrepresented attack types, preventnew/old class competition,
                                    and improve robustness under evolving label distributions.

                                    3.2.4. Confidence-Aware Pseudo-Label Filtering and Enhancement
                                         Indynamicintrusiondetectionundersemi-supervisedsettings,pseudo-labelquality
                                    directly affects the generalization performance of the model, especially for minority and
                                    ambiguous classes. Noisy pseudo-labels can mislead the learning process and amplify
                                    category bias in incremental training.  To address this, we propose a confidence-aware
                                    pseudo-labelfilteringmechanismthatintegratespredictionentropy,agreementconsistency,
                                    and temporal validation to ensure the reliability of unlabeled supervision.
```


### PDF page 10

[View original page, figures and tables](assets/page-010.png)

```text
Future Internet2025,17, 456                                                                                                                 10 of 25



                                          Entropy-BasedConfidenceFiltering: Givenanunlabeledsample x∈ DUt ,themodel
                                    computes its predicted class distribution p(y|x;θ), and corresponding prediction entropy

                                                                                 C∑
                                                                   H(x)=−           p(y= c|x)·logp(y= c|x).                                    (13)
                                                                                c=1

                                          We define a confidence thresholdτ, and retain only samples with low uncertainty

                                                                           ˆDUt  ={x∈ DUt | H(x)< τ}.                                               (14)

                                          This ensures that only high-confidence pseudo-labeled samples contribute to the
                                    unsupervised loss, thereby mitigating noise propagation in early training stages.
                                          Historical Consistency Verification: To further improve label reliability, we design a
                                    consistency-based verification mechanism. We compare the pseudo-labels generated by
                                    the current model fθt and the frozen model from the previous task fθt−1

                                                             Agree(x)= Iargmax fθt(x)= argmax fθt−1(x).                             (15)

                                          Only samples that satisfy both entropy confidence and inter-task agreement are re-
                                    tained for training. The final filtered pseudo-labeled set is

                                                               ˜DU∗t   ={x∈ DUt | H(x)< τ and Agree(x)= 1}.                              (16)

                                          Thisdual criterionhelpseliminateunstable ornewlyemergedboundary samplesthat
                                    might otherwise induce pseudo-supervision noise.
                                          Temporal Ensemble Smoothing: To stabilize predictions across tasks and training
                                    epochs,atemporalensemblepredictionstrategywasapplied,maintaininganexponential
                                    moving average of predictions for each unlabeled sample,

                                                                    ¯pt(x)= α· ¯pt−1(x)+(1−α)· p(y|x;θt).                                     (17)

                                    whereα∈[0,1] controlshistoricalmemory. Thisimproveslabelconsistencyacrosstraining
                                    rounds,especiallyforslowlyevolvingclasses. Thefilteredpseudo-labeledsamples  ˜DU∗t
                                    are used to compute the unsupervised loss term

                                                                        Lunsup =− ∑            logp(ˆyx|x;θ).                                            (18)
                                                                                       x∈ ˜DU∗t

                                          This revised loss ensures that only high-confidence, consistent pseudo-labels con-
                                    tributeto modelupdates, enhancinglearning stabilityand robustness inthe presenceof
                                    noisy, evolving data distributions.
                                          Algorithm1demonstratesthesemi-supervisedincrementallearningtrainingprocess
                                    driven by multi-layer alignment and meta-weighting.
```


### PDF page 11

[View original page, figures and tables](assets/page-011.png)

```text
Future Internet2025,17, 456                                                                                                                11 of 25



                                       Algorithm 1:The Proposed Framework
                                          Input: Previous round model fθt−1;Historical memoryMt−1;Current task dataDt;Loss
                                                  coefficient tupleλi for i∈{sup,unsup,align,meta};Learning rateη;Number of
                                                  training rounds E
                                          Output: Updated model fθt; Current round memoryMt
                                          //Step  1:    Update  dynamic  memory
                                        1 Mt← DPMeansUpdate(Mt−1,Dt);
                                          //Step  2:    Calculate  category  weights  and  biases

                                        2  According to the category frequency pc in the memory sample, obtain the weight
                                            wc = Softplus(MLP(pc)) through MLP;                  pc

                                        3  Calculate category bias bc = b(t−1)c      +η·log ∑k pk+ϵ  ;
                                          //Step  3:    Training  process

                                        4  for epoch= 1 to E do

                                        5        Sample training batchB fromDt∪Mt;

                                        6        Calculate the standard cross entropy loss (including the loss of unlabeled data with
                                                confidence-aware pseudo-label filtering and enhancement. see Equation (18)):
                                                LCE = λsupLsup+λunsupLunsup;

                                        7        Calculate the weighted loss:Lmeta =−λmeta∑cwcyclogpc;

                                        8        Calculate the hierarchical alignment loss:
                                        9          Llogits← KLdivergence(fθt−1, fθt);

                                       10          Lattn←  1L∑l∥Aoldl  − Anewl   ∥2F;

                                       11          Lbt←∑i(1−Cii)2+γ∑i̸=jC2ij;

                                       12          Lalign← λalign(Llogits+Lattn+Lbt);

                                       13        Update model parameters:

                                       14        θt← θt−1−η∇θ(LCE+Lmeta+Lalign);

                                       15  end
                                       16  returnFinal model fθt and memory setMt;

                                    4. Experiments
                                          Tocomprehensively evaluatethe performanceof theproposed frameworkin termsof
                                    catastrophicforgettingmitigation,minorityclassrecognition,androbustlearningunder
                                    labelscarcity,weconductextensiveexperimentsonmultiplereal-worldintrusiondetection
                                    datasets. Theeffectiveness ofour method isbenchmarked againstrepresentativebaselines
                                    acrossa varietyof metrics,includingclassification accuracy,forgetting rate,robustness to
                                    class imbalance, and training efficiency.

                                    4.1. Datasets and Evaluation Metrics
                                          We select three widely used intrusion detection datasets, UNSW-NB15 [34], CIC-
                                    IDS2017 [35], and TON_IoT [36], to simulate realistic multi-task, label-incomplete, and
                                    heterogeneousnetworkscenarios. Together,thesedatasetsofferadiverseandchallenging
                                    testbed for evaluating the proposed method’s adaptability and robustness.
                                          UNSW-NB15 dataset [34]:  This dataset is a new generation of network intrusion
                                    detection benchmark datasets proposed by the University of New South Wales, Australia,
                                    in 2015, aiming to overcome the limitations of traditional datasets (such as KDD99 and
                                    NSL-KDD)intermsofattacktypesandnetworkenvironments. Thisdatasetcontainsabout
                                    2.5millionnetworktrafficrecordsbymixingrealcampusnetworktrafficandsimulated
                                    attack data, covering 9 types of modern network attacks (such as vulnerability exploits,
                                    DoS,worms,Webattacks,etc.) andnormaltraffic,andprovides49finelydividednetwork
                                    trafficfeatures,includingbasic flowfeatures,trafficstatisticsfeatures,and contentfeatures.
                                    Comparedwithearlierdatasets,UNSW-NB15hassignificantadvantagesinthediversityof
                                    attack types and data balance and can better reflect the current network threat situation.
```


### PDF page 12

[View original page, figures and tables](assets/page-012.png)

```text
Future Internet2025,17, 456                                                                                                           12 of 25



                                   However,thisdatasetstillhastheproblemofinsufficientsamplesofsomeattackcategories,
                                   which may affect the generalization performance of the model in specific attack detection.
                                         CIC-IDS2017dataset[35]: Thisdatasetisacomprehensivenetworkintrusiondetec-
                                   tion benchmark dataset released by the Canadian Institute for Cyber Security in 2017. It
                                   represents one of the most advanced data benchmarks in the current field of network
                                   intrusion detection research. This dataset simulates 15 types of modern network attacks
                                   (including brute force cracking, DDoS, Web attacks, penetration attacks, and Heartbleed
                                   vulnerability attacks, etc.) in a real network environment, while collecting normal back-
                                   ground traffic, toconstruct a large-scaledataset containing about 2.8million network flow
                                   records. Comparedwithearlierdatasets,CIC-IDS2017providesmoreabundantnetwork
                                   traffic features, including flow duration, packet statistics, traffic behavior, and TLS/SSL
                                   encryptionfeatures,whichcanmorecomprehensivelyreflectthecharacteristicsofmodern
                                   networkthreats. Thedatasetisorganizedintimeseries,whichsupportsthestudyofattack
                                   evolution patterns and is particularly suitable for deep learning-based intrusion detection
                                   methods. However, this dataset has challenges such as large data size and unbalanced
                                   samples of some attack categories.  In practical applications, it is necessary to consider
                                   computing resource limitations and data balance issues. As one of the most comprehen-
                                   sive network intrusion detection benchmarks, CIC-IDS2017 is often used in conjunction
                                   with datasets such asUNSW-NB15, providingan importantreference forevaluating the
                                   performance of intrusion detection systems in modern complex network environments.
                                         TON_IoT dataset [36]: This dataset is a dedicated IoT security dataset developed
                                   by the Cyber Security Team of the University of New South Wales, Australia, and rep-
                                   resents one of the most advanced data benchmarks in the field of IoT threat detection.
                                   This dataset simulates a variety of typical attacks against IoT by building a real experi-
                                   mental environment containing smart home devices and industrial control systems (such
                                   as device hijacking, data leakage, ransomware, etc.) and collects about 22 million mul-
                                   timodal security data, covering network layer traffic (NetFlow/PCAP) and host layer
                                   logs(Windows/Linuxeventlogs). Comparedwithtraditionalnetworksecuritydatasets,
                                   the outstanding advantage of TON_IoT is that it is specially designed for IoT security
                                   scenarios. It notonlyincludesprotocol-level attacks (suchasMQTTspoofingand CoAP
                                   flooding) but also provides detailed attack stage annotations (reconnaissance, intrusion,
                                   andlateralmovement),supportingend-to-endattackbehavioranalysis. Thedatasetadopts
                                   a collaborative recording method of network traffic and host logs, providing unique data
                                   support for the study of cross-layer attack detection methods. However, this dataset has
                                   challenges such as large data size and unbalanced samples of some attack categories. In
                                   practical applications, computing resource optimization and data balance processing need
                                   to be considered. As one of the most comprehensive IoT security benchmarks currently,
                                   TON-IoT is often used in conjunction with datasets such as Bot-IoT [37], providing an
                                   important reference for evaluatingthe performance of intrusion detectionsystems in IoT
                                   environments, and is particularly suitable for the development of lightweight security
                                   models with limited resources.
                                         Foreachdataset,astandardizedpreprocessingpipelinewasappliedasfollows: Feature
                                   Selection and Normalization: We retained relevant numerical and categorical features for
                                   traffic statistics and flow behavior. Continuous features were normalized to [0, 1], and
                                   categorical features were one-hot encoded to reduce scale variance and stabilize training.
                                   HandlingMissingValues: Missingnumericalvalueswerereplacedwiththeclassmean,and
                                   missingcategorical valueswithan “UNK”tokento ensureconsistentinput dimensionality.
                                   Label Harmonization: Attack labels were harmonized across datasets. Synonymous attack
                                   types were mapped to unified categories following established taxonomies [34,35] to
                                   mitigatelabeling discrepancies. Incremental TaskSequence Construction: Eachdataset was
```


### PDF page 13

[View original page, figures and tables](assets/page-013.png)

```text
Future Internet2025,17, 456                                                                                                                           13 of 25



                                       partitioned into 5 sequential tasks based on chronological flow order, introducing new
                                       attack categories successively. To simulate blurred boundaries, 30–50% of samples were
                                       shared between consecutive tasks. Earlier tasks introduced 3–5 categories, while later tasks
                                       added 1-2, creating an imbalanced distribution. Label Scarcity Simulation: we randomly
                                       sampled 1%, 5%, 10%, and 20% of eachtask as labeled data, preserving class distribution,
                                       with the remainder unlabeled.
                                              AsshowninTable1,allthreedatasetsarestructuredtosimulateincrementalintrusion
                                       detection scenarios, where new attack classes are introduced progressively across task
                                       rounds. Each dataset exhibits different characteristics: UNSW-NB15 provides a relatively
                                       balanced baseline; CIC-IDS2017 emphasizes temporal sequence and class confusion; and
                                       TON_IoT introduces device heterogeneity and distribution shift, making them ideal for
                                       evaluating CL under varying real-world conditions.

                                       Table 1. Overview of datasets and incremental task settings.

                                         Dataset                           Type                                 Classes                   # Tasks    Label Ratio
                                         UNSW-NB15           Flow-based            10 (9 attack + 1 normal)           5                 10%
                                         CIC-IDS2017            Flow-based           15 (14 attack + 1 normal)         10                10%
                                         TON_IoT           IoT telemetry + Net    13 (12 attack + 1 normal)          7                 10%
                                       *Thedatasetsarestructuredtosimulateincrementallearningscenarios,wherenewattackclassesareintroduced
                                       progressivelyacrosstaskrounds. Eachdatasetexhibitsdifferentcharacteristics,makingthemidealforevaluating
                                       CLundervaryingreal-worldconditions. **Thelabelratioindicatestheproportionoflabeledsamplesavailable
                                       for each task, reflecting the challenges of label scarcity in real-world scenarios.

                                              Foreachdataset,wedefineasequenceofincrementaltasks,whereeachtaskintroduces
                                       a new subset of attack classes. The labeled data for each task is limited to 10% of the total
                                       samples, while the remaining 90% are treated as unlabeled. This setup reflects realistic
                                       scenarios where labeled data are scarce, and the model must rely on SSL techniques to
                                       leverage abundant unlabeled traffic.
                                              Table2illustratesthe task-wiseclass distribution forthe CIC-IDS2017dataset undera
                                       5-task incremental setting. Each task introduces a new set of attack types, with some tasks
                                       containing multiple classes to simulate realistic class overlap and confusion scenarios. This
                                       design allows us to evaluate the model’s ability to adapt to new threats while retaining
                                       knowledge of previously learned classes.

                                       Table 2. Task-wise class split for CIC-IDS2017 under 5-task incremental setting.

                                         Task ID     Classes Introduced (Attack Types with Quantity)
                                            T1          Normal (2,271,320), DDoS (128,025), PortScan (158,804)
                                            T2          Bot (1956), Web Attack-Brute Force (1507), Web Attack-XSS (652)
                                            T3          Infiltration (36), Heartbleed (11), Web Attack-Sql Injection (21)
                                            T4          FTP-Patator (7935), SSH-Patator (5897)
                                            T5          DoS {Hulk (230,124), GoldenEye (10,293), Slowloris (5796), Slowhttptest (5499)}
                                       * Each task introduces a new set of attack types, with some tasks containing multiple classes to simulate realistic
                                       class scenarios. This design allows us to evaluate the model’s ability to adapt to new threats while retaining
                                       knowledgeofpreviouslylearnedclasses. **Thequantitiesinparenthesesindicatethenumberofsamplesforeach
                                       class in the dataset; trainingand testing splits are performed accordingly. Supervised and unsupervised samples
                                       are drawnfrom these splits (mainly from the training set) based on the defined label ratio. For simplicity, only the
                                       total number of samples per class is shown here.

                                              Forquantitativeassessment,weadoptevaluationmetricsinTable3.  AverageAccu-
                                       racy (AA) measures overall classification performance across tasks; accuracy is defined as
                                       the ratio of correctly predicted samples to total samples, i.e., Accuracy =           TP+TNTP+TN+FP+FN,
                                       where TP, TN, FP, and FN represent true positives, true negatives, false positives, and
```


### PDF page 14

[View original page, figures and tables](assets/page-014.png)

```text
Future Internet2025,17, 456                                                                                                                             14 of 25



                                        falsenegatives,respectively. AveragePrecision(AP)measurestheprecisionacrosstasks;
                                        for a specific class, precision is definedas the ratio of truepositive predictions to the total
                                        predictedpositives,i.e., Precision=      TPTP+FP. AverageRecall(AR)measurestherecallacross
                                        tasks;foraspecificclass,recallisdefinedastheratiooftruepositivepredictionstothetotal
                                        actualpositives,i.e., Recall =      TPTP+FN. F1-Score(F1)balancesprecisionandrecall,calculated
                                        as the harmonic mean ofprecision and recall, i.e., F1=  2·Precision·RecallPrecision+Recall . Forgetting Measure
                                        (FM) quantifies the degree of catastrophic forgetting on previous tasks. Backward Transfer
                                        (BWT) assesses the influence of learning new tasks on old tasks. Imbalance Robustness
                                        (IR)evaluatesperformanceconsistencyacrossimbalancedclasses. MinorityRecall(MR)
                                        focusesonthedetectionrateofminorityclasses. Top-kError(Top-k)assessesmulti-class
                                        confusion detection.

                                        Table 3. Evaluation indicator definition description.

                                          Metric                                Abbreviation    Formula
                                          Average Accuracy                     AA             AAt =  1t ∑ti=1 Ati
                                          Average Precision                      AP              APt =  1t ∑ti=1Pti
                                          Average Recall                           AR              ARt =  1t ∑ti=1Rti
                                          F1-Score                                       F1              F1t =  1   2·Pti·Rti
                                                                                                           t ∑ti=1   Pti+Rti
                                          Forgetting Measure                   FM              FMt =    1t−1∑t−1i=1       maxj<t Aji− Ati
                                          Backward Transfer                   BWT            BWTt =  1t ∑ti=1(Aii− Ati)
                                          Imbalance Robustness               IR               IR=  minc Acccmaxc Accc
                                          Minority Recall                          MR             MR=    1                   TPc
                                                                                                            |Cm|∑c∈Cm     TPc+FNc
                                          Top-k Error                               Top-k           Top-k= 1−  1N∑Ni=1I(yi∈ Topk(f(xi)))
                                        * Where Ati represents the accuracy on task i after the tth round of training, Pti and Rti represent the precision and
                                        recall on task i after the tth round of training, respectively. Accc is the accuracy for class c, and TPc and FNc are
                                        thetruepositive andfalse negativeexamples ofcategory c, respectively. AAmeasures theoverall classification
                                        performance of the model, AP measures the precision of the model, AR measures the recall of the model, and
                                        F1 balances precision and recall, providing a comprehensive performance metric.  FM reflects the degree of
                                        catastrophicforgetting,BWTmeasuresbackwardtransferstability,IRevaluatesimbalancerobustness,MRfocuses
                                        on minority class detection, and Top-k assesses multi-class confusion detection.

                                        4.2. Baselines
                                              Toverifytheeffectivenessofthemethodsproposed,thispaperselectsrepresentative
                                        comparisonmethodsunderthecurrentmainstreamCL,SSL,andthefusionparadigmof
                                        the two to construct a systematic experimental control group. All baseline methods are
                                        uniformly reproduced orreused underthe samedata division andtask sequence toensure
                                        the fairnessand reliabilityof the comparison. Model classificationand core strategiesare
                                        shown in Table4.

                                        Table 4. Baselines.

                                          Category     Method             Core Strategy

                                          IL                  iCaRL [11]        Memory sample + Prototype classifierIL2M [38]          Dual memory + Outputcalibration

                                          SSL               FixMatch[24]   High confidence pseudo-label + Consistency constraint

                                          SSL + IL       SSIL [39]           Incremental distillation + Reconstruction errorPLCiL [30]             Hybrid label modeling + Dynamic pseudo-label correction

                                        *ILreferstoIncrementalLearning,SSLreferstoSemi-SupervisedLearning,andtheircombinationisdenotedas
                                        SSL + IL.
```


### PDF page 15

[View original page, figures and tables](assets/page-015.png)

```text
Future Internet2025,17, 456                                                                                                              15 of 25



                                          In the face of various complex experimental settings, not all comparison methods are
                                    applicable. TheapplicabilitydescriptionisshowninTable5. Asthebasisfortherationality
                                    of the experimental design. In the subsequent experimental result tables, for methods that
                                    donotsupporttherelevantsettings,theirresultsareuniformlymarkedas“×”or“N/A”,
                                    and the reasons are stated in the table notes.

                                    Table 5. Applicability of comparison methods under different experimental settings.

                                     Method                        IL               SST           LST           DLS          MCV         ETS
                                     iCaRL                 ✓          ×         ✓          ×          △         ✓
                                     IL2M                  ✓          ×         ✓          ×         ✓         ✓
                                     FixMatch               ×         ✓          ×         ✓          ×          ×
                                     SSIL/PLCiL/Ours   ✓         ✓         ✓         ✓         ✓         ✓
                                   *✓indicatesthatthemethodisapplicabletotheexperimentalsetting;△indicatesindirectadaptation;×indicates
                                    thatthemethoddoesnotsupportortheoriginaldesigncannotadapttothissetting. **ILstandsforIncremental
                                    Learning. SSTstandsforSemi-supervisedTraining. LSTstandsforLongSequenceTask. DLSstandsforDynamic
                                    Label Scale. MCV stands for Memory Capacity Variation. ETS stands for Extreme Task Sequence.

                                    4.3. Implementation Details
                                          TheproposedframeworkisimplementedusingPyTorch(withversion1.13.1),withthe
                                    followingkeyhyperparameters: Memorysize: 5000samplespertask,dynamicallyadjusted
                                    based on the number of classes; DP-Means clustering threshold: 0.5, controlling cluster
                                    granularity;Uncertaintysampling: Top-20%sampleswithhighestentropyselectedfrom
                                    unlabeleddata;Lossweights: λ={1.0,0.5,0.5}forbalancingalignmentlosses,λmeta = 1.0
                                    for meta-weighted loss; Learning rate: 0.001 for Adam optimizer, with cosine annealing
                                    schedule; Batch size: 128 for labeled data, 256 for unlabeled data.
                                          Themodelarchitectureconsistsofafeatureextractorfollowedbyamulti-layerpercep-
                                    tron head for classification. The attention mechanism is implemented using self-attention
                                    layers to capture critical fields in network traffic data.
                                          The modelis trainedfor 100epochs pertask, withearly stoppingbased on validation
                                    accuracytopreventoverfitting. Thememorybufferisupdatedaftereachtask,retaining
                                    the most representative samples according to the DP-Means clustering and uncertainty
                                    sampling strategy.
                                          For a fair comparison, we carefully designed the training protocols for all baseline
                                    methods and our proposed framework. Specifically, for methods that are originally de-
                                    signedforCLbutdonotsupportsemi-supervisedsettings(e.g.,iCaRL,IL2M),wefollowed
                                    the same incremental task protocol as our method but only used the labeled subset of each
                                    task,whichwasrestrictedto10%ofthetotaltrainingdata. Thisensuresthatthesemethods
                                    operate under the same label-scarce condition as our framework.
                                          For SSL methods that are not inherently continual (e.g., FixMatch), we trained the
                                    model with both labeled and unlabeled data within each task, but without the incremental
                                    extensionacrosstasks. Thisprovidesastrongsemi-supervisedbaselinewhilekeepingthe
                                    comparison fair in terms of data utilization.
                                          For ourproposed framework,we integrated both continual and semi-supervised com-
                                    ponents: Labeleddata(10%pertask)wereusedwithsupervisedloss,whiletheremaining
                                    unlabeled data were incorporated via pseudo-labeling and consistency regularization.

                                    4.4. Results and Analysis
                                          Figure2and Table6present the detailed experimental results on the UNSW-NB15,
                                    CIC-IDS2017, and TON_IoT datasets, respectively.  From these tables, it is evident that
                                    the proposed framework consistently achieves the best overall performance across all
                                    three benchmark intrusion detection datasets. This demonstrates its strong adaptability
```


### PDF page 16

[View original page, figures and tables](assets/page-016.png)

```text
Future Internet2025,17, 456                                                                                                              16 of 25



                                                                 and robustness in addressing realistic challenges, including multi-task CL, label scarcity,
                                                                 andclassimbalance. Specifically,ourframeworkattainsclassificationaccuraciesof85.6%
                                                                 on UNSW-NB15, 83.4% on CIC-IDS2017, and 81.7% on TON_IoT—each surpassing the
                                                                 currentstrongestbaselinemethod(PLCiL)bymorethan5%points. Theseimprovements
                                                                 indicatetheframework’sstablelearningcapabilityunderdynamictasksequencesanddata
                                                                 distributions. To further illustrate the advantages of our method, we provide a detailed
                                                                 analysis of key metrics below.  AA: Our method consistently outperforms all baselines
                                                                 across datasets, achieving significant gains of 4-5% over the next best method (PLCiL).
                                                                 This highlights its superior ability to learn and retain knowledge across incremental tasks.
                                                                 FM: The proposed framework exhibits the lowest forgetting rates, indicating effective
                                                                 mitigationofcatastrophicforgetting. Themulti-layeralignmentandmeta-weightedloss
                                                                 componentscontributetothisstability. MR:Ourapproachachievesthehighestrecallon
                                                                 minority classes, demonstrating its robustness inhandling class imbalance. Thedynamic
                                                                 memoryupdateanduncertainty-basedsamplingstrategiesplayacrucialroleinenhancing
                                                                 minority class detection.  IR: The framework shows superior performance consistency
                                                                 across imbalanced classes,with IR values significantlyhigher than baselines. This reflects
                                                                 itsabilitytogeneralizewellevenunderskewedclassdistributions. Top-3: ThelowestTop-3
                                                                 error rates indicate that our method effectively reduces multi-class confusion, which is
                                                                 critical in intrusion detection scenarios with overlapping attack characteristics.


















                                                                                                              (a) UNSW-NB15


















                                                                              (b) CIC-IDS2017                                                    (c) TON_IoT
                                                                                    − iCaRL − IL2M − FixMatch − SSIL − PLCiL − Ours

                                                                 Figure 2. Performance on three datasets.

                                                                       Table6summarizes the key performance metrics across all datasets.  A high Avg-
                                                                 Precisionindicatesalowfalsealarm rate(fewbenignsamplesaremisclassifiedasattacks),
                                                                 and a high Recall indicates a low missed detection rate (few attacks are misclassified as

                  AA↑AA↑AA↑                                      benign). OurmethodachievesanoutstandingF-scoreof84.3%onUNSW-NB15,82.1%on
                   85.6
                   83.4
                   81.7
     Top-3↓Top-3↓Top-3↓      AP↑AP↑AP↑
        15.616.1             84.9
        17.1                 81.082.7



MR↑MR↑MR↑69.164.763.2            79.581.583.7AR↑AR↑AR↑

 100100100838383676767505050333333171717




    91.087.082.0               80.182.184.3
  IR↑IR↑IR↑                       F1↑F1↑F1↑



                        12.59.48.7
           BWT↑BWT↑BWT↑3.7FM↓FM↓FM↓
            97.92.9
```


### PDF page 17

[View original page, figures and tables](assets/page-017.png)

```text
Future Internet2025,17, 456                                                                                                                            17 of 25



                                        CIC-IDS2017,and80.1%onTON_IoT,whichimpliesthatbothitsPrecisionandRecallare
                                        high. Thisallowsustoconfidentlystatethatthehighaccuracyofourmodelisnotachieved
                                        by sacrificing one metric for the other but represents a robust balance between minimizing
                                        both false alarms and missed detections.
                                              Figure2apresentsadetailedbreakdownofperformancemetricsontheUNSW-NB15
                                        dataset. Our frameworknot onlyexcelsin AAbut alsodemonstratessignificant reductions
                                        inFMandimprovementsinMR.TheBWTmetricindicatesthatlearningnewtaskshasa
                                        less detrimental effect on previously learned tasks compared to baselines, showcasing the
                                        stability of our approach.

                                       Table 6. Experimental results on three datasets: UNSW-NB15, CIC-IDS2017, and TON_IoT.

                                             Dataset           Method      AA      AP      AR       F1       FM      BWT       IR      MR     Top-3
                                                               iCaRL        76.2     75.5     74.3     74.9     18.7    −7.4      0.67     46.1      25.3
                                                               IL2M        78.0     77.3     76.1     76.7     16.3    −6.1      0.70     49.8      22.9
                                         UNSW-NB15           FixMatch     75.3     74.6     73.2     73.8    ×       ×        0.62     44.2      27.1
                                                                SSIL         80.7     80.1     78.9     79.5     12.1    −4.5      0.76     57.9      19.8
                                                               PLCiL        78.5     77.8     76.4     77.1     13.9    −4.8      0.83     55.9      21.3
                                                               Ours         85.6     84.9     83.7     84.3      8.7     −2.1      0.90     64.7      15.6
                                                               iCaRL        70.3     69.8     68.5     69.1     22.4    −9.1      0.67     42.4      30.5
                                                               IL2M        73.9     73.2     71.8     72.5     19.8    −7.6      0.70     45.2      28.3
                                          CIC-IDS2017        FixMatch     72.8     72.1     70.7     71.4    ×       ×        0.62     43.1      29.7
                                                                SSIL         77.8     77.1     75.9     76.5     14.7    −5.2      0.81     54.2      22.4
                                                               PLCiL        78.6     77.9     76.7     77.3     13.5    −4.8      0.83     55.9      21.3
                                                                Ours         83.4     82.7     81.5     82.1      9.4     −2.9      0.91     63.2      17.1
                                                               iCaRL        68.5     67.9     66.4     67.0     25.1   −10.3     0.65     43.2      33.8
                                                               IL2M        70.4     69.7     68.2     68.8     22.8    −8.7      0.68     47.4      30.5
                                            TON_IoT          FixMatch     69.7     69.0     67.5     68.1    ×       ×        0.60     39.7      26.5
                                                                SSIL         75.3     74.6     73.1     73.7     18.4    −6.1      0.75     56.1      22.9
                                                               PLCiL        76.9     76.2     74.7     75.3     16.9    −5.4      0.78     59.7      21.7
                                                                Ours         81.7     81.0     79.5     80.1     12.5    −3.7      0.88     69.1      16.1
                                        × indicates that the metric is not applicable. The bold font highlights the best performance in each metric.

                                              Figure3a–d illustrate the performance trends of each method across different task
                                        sequencesontheCIC-IDS2017dataset. Ourproposedframeworkconsistentlyoutperforms
                                        all baselinesin AA, demonstratingits superior learningand retention capabilities. Addi-
                                        tionally,itmaintainsthelowestFMvalues,indicatingeffectivemitigationofcatastrophic
                                        forgetting. The MR metricshows that ourmethod excelsin recognizing minority classes,
                                        acriticalaspectinintrusiondetectionscenarios. Finally,theF1-Scoretrendsfurthervali-
                                        date the robustness and reliability of our approach across sequential tasks. The detailed
                                        numerical results are provided in Table7.
                                              To comprehensivelyassess thestabilityandadaptabilityofourframeworkindiverse
                                        and complex deployment scenarios, we design an extended set of experiments along
                                        the four axes below.  Catastrophic Forgetting Analysis under Varying Task Sequence
                                        Lengths: Evaluatehowthemodelretainspriorknowledgeasthenumberofsequentialtasks
                                        increases, simulating long-term deployment. Semi-Supervised Robustness under Varying
                                        Labeled Sample Ratios: Test the model’s sensitivity to supervision sparsity by adjusting
                                        the ratio of labeled samples available per task. Memory-Efficient Knowledge Retention
                                        under Varying Buffer Sizes: Investigate the trade-off between memory constraints and
                                        knowledgepreservationbyalteringthereplaybuffercapacity. StressTestingunderExtreme
                                        Scenarios: Analyzemodelbehaviorunderchallengingconditions—e.g.,unbalancedtask
                                        orders, adversarial class overlap, and label scarcity—designed to simulate worst-case
                                        real-world settings.
```


### PDF page 18

[View original page, figures and tables](assets/page-018.png)

```text
Future Internet2025,17, 456                                                                                                                                                18 of 25



                                                            Table 7.  Experimental results during the training process under different task sequences on the
                                                            CIC-IDS2017 (under 3 task sequences).

                                                              Task       Method        AA         AP         AR          F1          FM       BWT        IR         MR      Top-3
                                                                            iCaRL         76.7        76.0        74.6        75.3        17.5     −6.8       0.69        47.3        26.1
                                                                            IL2M          77.2        76.5        75.1        75.8        14.8     −5.6       0.70        48.9        24.3
                                                                T1        FixMatch      72.5        72.0        70.6        71.3      ×        ×          0.62        43.1        29.7
                                                                             SSIL           76.8        76.1        74.7        75.4        15.6     −5.9       0.76        52.1        23.1
                                                                            PLCiL         78.5        77.8        76.4        77.1        13.9     −4.8       0.83        55.9        21.3
                                                                            Ours           85.0        84.5        83.1        83.8        10.5     −3.0       0.90        63.0        19.0
                                                                            iCaRL         74.1        73.4        72.0        72.7        20.5     −8.1       0.65        44.0        29.1
                                                                            IL2M          74.3        73.6        72.2        72.9        20.1     −7.4       0.65        44.1        28.7
                                                                T2        FixMatch      70.8        70.2        68.8        69.5      ×        ×          0.60        41.3        30.1
                                                                             SSIL           75.1        74.4        73.0        73.7        16.2     −5.5       0.74        50.3        24.7
                                                                            PLCiL         76.3        75.6        74.2        74.9        15.1     −4.9       0.79        53.1        22.8
                                                                             Ours          81.2        80.5        79.1        79.8        11.8     −3.2       0.88        60.5        21.1
                                                                            iCaRL         72.5        71.8        70.4        71.1        22.7     −8.9       0.63        40.5        30.8
                                                                            IL2M          73.4        72.7        71.3        72.0        21.3     −8.2       0.64        42.3        29.4
                                                                T3        FixMatch      69.2        68.6        67.2        67.9      ×        ×          0.58        39.7        31.5
                                                                             SSIL           73.5        72.8        71.4        72.1        18.3     −6.3       0.72        48.7        25.9
                                                                            PLCiL         75.1        74.4        73.0        73.7        16.7     −5.1       0.81        51.6        23.9
                                                                             Ours          78.9        78.2        76.8        77.5        13.2     −3.5       0.85        57.1        22.4
                                                            × indicates that the metric is not applicable. The bold font highlights the best performance in each metric.












                                                                              (a) AA Performance                                                     (b) FM Performance











                                                                              (c) MR Performance                                                      (d) F1 Performance
                                                               −•−iCaRL   −■−IL2M   −▲−FixMatch   −♦−SSIL   −⊕−PLCiL   −⋆−Ours

                                                            Figure 3. Performance evolution across task sequences on CIC-IDS2017 dataset under 3 tasks.

                                                                   These extended evaluations offer a holistic perspective on the proposed framework’s
                                                            real-world readiness, demonstrating not only strong average-case performance but also
                                                            resilience to domain shift and resource constraints.
                                                                   Table8summarizestheperformancevariationsineachmethodunderdifferentlabeled
                                                            sample ratios.  As expected, all models demonstrate improved accuracy and MR with
                                                            increasing supervision levels. However, the proposed framework consistently maintains
                                                            strong recognition capability even under extremely limited supervision.  Notably, at a
                                                            1% label ratio, our framework achieves an MR of 60.1%, significantly outperforming all
                                                            baseline methods. This result highlights the framework’s ability to effectively leverage
                                                            unlabeleddatathroughitsmulti-levelalignmentandconfidence-awarepseudo-labeling

90709025                                                    mechanisms. Moreover,themodeldemonstratessuperiorperformanceonbothMRand

          83.88563
                           60.5
60                         81.2              57.1
20                         79.8
8080                                         78.9
                                             77.5

50
15                                           13.2
                           11.8
7070      10.5
40
10

          T1T1T1T1          T2T2T2T2         T3T3T3T3
```


### PDF page 19

[View original page, figures and tables](assets/page-019.png)

```text
Future Internet2025,17, 456                                                                                                                                                     19 of 25



                                              IRacrossallsettings,showcasingitsresiliencetoclass imbalanceandlabelsparsity—two
                                              pervasive challenges in real-world intrusion detection.
                                                     These findings suggest that our framework is particularly well-suited for weakly
                                              superviseddeploymentscenarios,suchasindustrialcontrolsystemsandIoTenvironments,
                                              where high-quality labels are scarce and costly to obtain.
                                                     Table9shows the disaster forgetting performance of the proposed method and the
                                              comparison method under different memory capacity settings. It can be seen that as the
                                              memory capacity increases, the accuracy of all methods is improved, but this method
                                              can stillmaintain alow forgetting rateand ahigh minority classrecall rateunder a small
                                              memory capacity and can store more representative class center samples and boundary
                                              information, which is suitable for resource-constrained edge device scenarios.

                                              Table 8. Model performance under different label ratios on the UNSW-NB15 dataset.

                                                Label      Method        AA         AP         AR          F1          FM       BWT        IR         MR      Top-3
                                                              iCaRL         67.4        66.1        64.8        65.4        21.5     −9.2       0.63        40.2        28.5
                                                               IL2M          66.9        65.2        64.0        64.6        21.0     −9.0       0.64        50.1        28.7
                                                  1%        FixMatch      65.4        63.8        62.5        63.1      ×        ×          0.48        38.5        29.2
                                                                SSIL           71.2        69.5        68.3        68.9        18.9     −9.5       0.62        51.7        27.5
                                                              PLCiL         73.5        71.8        70.5        71.1        16.7     −9.3       0.65        53.3        30.5
                                                               Ours           77.1        76.4        75.1        75.7        11.3     −5.1       0.73        60.1        28.7
                                                              iCaRL         72.8        70.9        69.5        70.1        20.3     −8.7       0.65        43.3        27.1
                                                               IL2M          73.4        71.9        72.5        72.2        18.9     −7.5       0.68        49.5        26.3
                                                  5%        FixMatch      71.5        69.8        68.4        69.1      ×        ×          0.58        45.1        28.1
                                                                SSIL           76.3        74.7        73.5        74.1        14.4     −6.2       0.70        56.2        24.5
                                                              PLCiL         77.9        75.2        74.0        74.6        12.2     −4.3       0.73        57.6        22.5
                                                               Ours          82.6        81.9        80.6        81.2         9.7     −2.8       0.80        64.7        19.8
                                                              iCaRL         74.1        72.8        71.6        72.2        20.1     −8.3       0.66        45.9        26.3
                                                               IL2M          75.2        73.9        74.5        74.2        17.5     −7.1       0.69        49.8        25.7
                                                 10%        FixMatch      73.2        71.5        70.7        71.4      ×        ×          0.61        47.9        27.2
                                                                SSIL           78.1        78.5        77.2        77.8        13.3     −4.6       0.74        58.5        22.9
                                                              PLCiL         79.5        78.8        77.5        78.1        11.5     −3.5       0.76        60.3        18.7
                                                               Ours          83.9        83.2        81.9        82.5         9.1     −2.4       0.83        67.4        17.1
                                                              iCaRL         76.2        75.5        74.3        74.9        18.7     −7.4       0.68        46.1        25.3
                                                               IL2M          78.0        77.3        76.1        76.7        16.3     −6.1       0.70        49.8        22.9
                                                 20%        FixMatch      75.3        74.6        73.2        73.8      ×        ×          0.65        44.2        27.1
                                                                SSIL           80.7        80.1        78.9        79.5        12.1     −4.3       0.78        57.9        19.8
                                                              PLCiL         81.5        80.8        79.6        80.2        11.6     −3.8       0.80        59.8        18.7
                                                               Ours          85.6        84.9        83.7        84.3         8.7     −2.1       0.82        64.7        15.6
                                              × indicates that the metric is not applicable. The bold font highlights the best performance in each metric.


                                              Table 9. Comparison of catastrophic forgetting under different memory capacities.

                                                Memory Capacity     Method     AA      AP      AR       F1       FM     BWT      IR      MR     Top-3

                                                          1000                   iCaRL      70.5     67.5     66.3     66.9     22.1   −9.1     0.55     41.6      33.2Ours        72.3     71.3     70.1     70.7     10.9   −4.3     0.71     58.6      23.7


                                                          3000                   iCaRL      73.4     70.5     69.3     69.9     18.6   −8.0     0.63     45.7      28.1Ours       82.3     80.1     78.9     79.5      9.3    −3.1     0.77     61.3      19.4


                                                          5000                   iCaRL      76.2     75.5     74.3     74.9     18.7   −7.4     0.68     46.1      25.3Ours       85.6     84.9     83.7     84.3      8.7    −2.1     0.82     64.7      15.6

                                              The bold font highlights the best performance in each metric.

                                                     Table10presentsthe performance ofour proposed frameworkunder varying degrees
                                              of class imbalance on the CIC-IDS2017 dataset. The experiments are designed to simulate
                                              real-world scenarios where certain attack types are significantly underrepresented com-
                                              paredtoothers,posingchallengesforeffectiveintrusiondetection. Inthebalancedscenario
```


### PDF page 20

[View original page, figures and tables](assets/page-020.png)

```text
Future Internet2025,17, 456                                                                                                                                     20 of 25



                                          (10:10:10),our methodachievesanAA of82.3%,demonstratingits abilitytomaintainhigh
                                          accuracy across all classes. The FM of 12.1 indicates a low level of catastrophic forgetting,
                                          while the MR of 62.5% highlights the model’s effectiveness in identifying minority classes.
                                          As the class imbalance increases to 10:50:50, the AA slightly decreases to 78.7%, but the
                                          modelstillmaintainsarobustperformancewithanFMof13.4andanMRof56.3%. This
                                          suggests that our framework can adapt to moderate class imbalance without significant
                                          degradationin performance. Inthe more extreme imbalancescenario of10:100:100, theAA
                                          furtherdecreasesto73.4%,withanFMof15.2andanMRof50.2%. Despitethechallenges
                                          posedby severeclass imbalance, our method continuesto outperformbaseline approaches,
                                          indicating its resilience and adaptability. Finally, in the most severe imbalance scenarios
                                          (50:100:100, 100:100:100, and 100:100:500), the AA drops to 61.1%, with corresponding
                                          increases in FM and decreases in MR. However, even under these challenging conditions,
                                          our framework demonstrates a commendable ability to detect minority classes, as evi-
                                          dencedby theMRof 38.5%inthe 100:100:500scenario. Overall,these resultsunderscore
                                          the robustness of our proposed framework in handling class imbalance, making it a viable
                                          solution for real-world intrusion detection tasks where data distribution is often skewed.

                                          Table 10. Robustness results under different class imbalance on the CIC-IDS2017 dataset under 3
                                          tasks.

                                            Imbalance Ratio      Method      AA      AP      AR       F1       FM      BWT       IR      MR     Top-3
                                                                       iCaRL        78.4     77.3     73.5     75.7     15.8    −6.3      0.72     52.3      22.5
                                                                        IL2M        80.1     79.0     75.2     77.1     14.3    −5.8      0.74     54.1      21.3
                                                 10:10:10            FixMatch     74.2     73.1     69.3     71.1    ×       ×        0.60     48.3      26.7
                                                                        SSIL         79.2     78.1     74.3     76.2     14.9    −5.9      0.75     55.8      20.1
                                                                       PLCiL        81.1     80.0     76.2     78.1     13.5    −4.8      0.83     60.3      18.7
                                                                       Ours         82.3     81.2     77.4     79.3     12.1    −4.1      0.85     62.5      17.3
                                                                       iCaRL        72.5     71.4     68.6     70.0     17.5    −7.9      0.53     49.8      27.2
                                                                        IL2M        71.8     70.7     67.9     69.3     16.8    −7.1      0.55     50.9      25.3
                                                 10:50:50            FixMatch     68.3     67.2     64.4     65.8    ×       ×        0.45     44.1      30.5
                                                                        SSIL         73.5     72.4     69.6     71.0     16.2    −6.5      0.60     51.7      24.1
                                                                       PLCiL        75.4     74.3     71.5     72.9     14.8    −5.3      0.65     53.9      22.8
                                                                        Ours         78.7     77.6     74.8     76.2     13.4    −4.5      0.68     56.3      20.5
                                                                       iCaRL        63.2     62.1     60.3     61.2     23.5   −11.8     0.43     35.7      38.1
                                                                        IL2M        61.5     60.4     58.6     59.5     22.8   −10.3     0.47     36.5      35.2
                                                10:100:100           FixMatch     53.8     52.7     50.9     51.8    ×       ×        0.38     26.1      40.5
                                                                        SSIL         67.4     66.3     64.5     65.4     20.1    −8.2      0.55     42.3      30.2
                                                                       PLCiL        66.9     65.8     64.0     65.0     19.3    −7.5      0.58     44.7      28.9
                                                                        Ours         73.4     72.3     70.5     71.4     15.2    −5.1      0.65     50.2      25.7
                                                50:100:100               Ours         71.3     70.2     68.4     69.3     16.8    −5.9      0.62     48.7      27.3
                                               100:100:100              Ours         67.7     66.6     64.8     65.7     19.4    −7.2      0.58     44.3      30.1
                                               100:100:500              Ours         61.1     60.0     58.2     59.1     22.7   −10.5     0.49     38.5      35.7
                                          *× indicates that the metric is not applicable. The bold font highlights the best performance in each metric. The
                                          imbalance ratio calculates the ratio of the number of samples in the majority class to the number of samples in the
                                          minority class for each task. For example, 10:1:1 indicates that in the first task, the majority class has 10 times the
                                          numberofsamplesasthe minority class,while50:1:1indicatesamoresevere imbalance,withthemajorityclass
                                          having50timesthesamplesoftheminorityclass. **Toavoidineffectivelearningduetoextremeclassimbalance,
                                          weset aminimum thresholdof N samplesfor theminority classin eachtask. Some attacktypes withfewer than
                                          N samplesareexcludedfromtheexperiments. Thensplitthedatasetinto3tasksrandomly,thendeterminethe
                                          number of samples for each class in each task based on the specified imbalance ratio, i.e., for a 10:1:1 ratio, if the
                                          minorityclasshas800samples,themajorityclasswillhave8000samples. ***Allmethodsarereproducedand
                                          compared under the same experimental settings to ensure fairness.

                                                 Table11presentstheperformanceofourproposedframeworkundervariousextreme
                                          scenariosdesignedtotestitsrobustnessandadaptability. Eachscenariosimulateschalleng-
                                          ingreal-worldconditionsthatanintrusiondetectionsystemmightencounter. In theESTE
                                          scenario,themodeldemonstratesstrongstabilitywithanAAof75.8%andalowFMof7.9,
```


### PDF page 21

[View original page, figures and tables](assets/page-021.png)

```text
Future Internet2025,17, 456                                                                                                               21 of 25



                                    indicatingitsabilitytoretainknowledgeoverprolongedperiodsofminimalchange. The
                                    MRof62.1%furtherhighlightsitseffectivenessinidentifyingrareattacktypesevenwhen
                                    task changes are infrequent. In the FTC scenario, themodel achieves an AA of 79.7%and
                                    an FM of 13.4, showcasing its capacity to quickly adapt to rapidly evolving threats. The
                                    MRof59.9%indicatesthatwhilethemodeladaptsquickly,itstillmaintainsareasonable
                                    level of performance on minority classes. The NICD scenario tests the model’s ability to
                                    handle unevendata flows,where it achievesan AAof 77.3% andan FMof 12.7. The high
                                    MR of64.2% suggests thatthe model effectively managesclass imbalance, ensuringthat
                                    minorityclasses arenot overlooked. Finally,in theEFLR scenario,the modelmaintains an
                                    AA of 78.5% and an FM of 12.1, demonstrating resilience to significant label noise. The MR
                                    of60.3%indicatesthatthemodelcanstillidentifyminorityclassesdespitefluctuationsin
                                    labelquality. Overall,theseresultsunderscoretherobustnessofourproposedframework
                                    acrossarangeofchallengingconditions,makingitwell-suitedfordeploymentindynamic
                                    and unpredictable network environments.

                                    Table 11. Robustness results under extreme experimental settings.

                                      Experiments     AA     AP      AR      F1      FM     BWT      IR      MR    Top-3
                                      ESTE                  75.8    74.1    72.9    73.5     7.9    −2.1     0.79    62.1      18.7
                                      FTC                    79.7    78.5    77.3    77.9    13.4   −4.3     0.73    59.9      22.4
                                      NICD                77.3    76.1    74.9    75.5    12.7   −3.8     0.77    64.2      20.3
                                      EFLR                 78.5    77.3    76.1    76.7    12.1   −3.5     0.75    60.3      21.3
                                    * This table scenario is constructed based on the TON_IoT dataset. ** ESTE is the extreme task evolution scenario,
                                    wherethemodelneedstoadapttoextremelyslowtaskchanges;FTCisthefasttaskchangescenario,wherethe
                                    model needs to quickly adapt to new tasks. NICD is the non-independent category distribution scenario, where
                                    the modelneeds tohandle unevendata flows. EFLR isthe extremefluctuation of thelabel ratioscenario, where
                                    the model needs to cope with significant label noise.

                                    4.5. Ablation Study
                                          To evaluate thecontribution of each componentwithin the proposed framework,we
                                    designasetofsystematicablationexperiments. Byremovingorreplacingspecificmodules,
                                    we observethe changes in keyperformance metrics such asoverall accuracy, catastrophic
                                    forgetting, category robustness, and minority class recall to analyze the effectiveness and
                                    necessityofeachsub-moduleindynamicintrusiondetection. Allablationexperimentsare
                                    conducted on the CIC-IDS2017 dataset. The task sequence is divided into 5 incremental
                                    rounds, with a 10% labeled sample ratio and a fixed memory buffer size of 5000.  All
                                    other hyperparameters remain consistent with those used in the main experiments to
                                    ensure a fair comparison. The details of each configuration are introduced below. Full
                                    Model:  keep the complete proposed framework, including all components.  w/o Multi-
                                    LevelDistillation: removeattentionalignmentandfeature-leveldistillation. w/oDP-Means
                                    Memory: replacetheDP-Means+entropy-basedmemoryselectionwithrandomsampling
                                    (reservoir sampling).  w/o Meta-Weighting:  remove the category frequency-driven loss
                                    weight and bias adjustment, treating all classes equally.  w/o Semi-Supervised Learning:
                                    completely remove the unlabeled data and train only on labeled samples, thus disabling
                                    the SSL mechanism. w/o Pseudo-Labeling: remove the confidence-aware pseudo-labeling
                                    mechanism.
                                          Table12presents the results of the ablation experiments, highlighting the impact
                                    of each component on the overall performance of the proposed framework.  The full
                                    model consistently outperforms all ablated versions across key metrics, demonstrating
                                    the effectiveness of each module in enhancing dynamic intrusion detection. Removing
                                    the multi-level distillation module results in a significant drop in AA to 79.2% and an
                                    increase in FM to 13.7, indicating that knowledge retention across tasks is compromised
```


### PDF page 22

[View original page, figures and tables](assets/page-022.png)

```text
Future Internet2025,17, 456                                                                                                               22 of 25



                                    without this component. The MR also decreases to 59.6%, underscoring the importance
                                    of multi-level feature alignment in recognizing rare attack types. The absence of the DP-
                                    Means memory selection strategy leads to a further decline in performance, with AA
                                    droppingto78.6%andFMrisingto15.1. Thissuggeststhateffectivememorymanagement
                                    iscrucialfor maintaining modelstabilityandperformanceover time. Excluding themeta-
                                    weighting mechanism has a pronounced effect on IR, which falls to 0.71, and MR decreases
                                    to52.4%. Thishighlightstheroleofclass-awareoptimizationinaddressingclassimbalance
                                    and ensuring equitable learning across categories. The removal of the semi-supervised
                                    learning component results in the most substantial performance degradation, with AA
                                    falling to 74.9% and FM increasing to 17.4. The MR drops to 49.1%, indicating that the
                                    modelstrugglestolearneffectivelyfromlimitedlabeleddatawithoutleveragingunlabeled
                                    samples. Finally, eliminating the pseudo-labeling mechanism leads to a decrease in AA
                                    to 81.3% and an increase in FM to 10.7, demonstrating that confident pseudo-labeling
                                    contributes significantly to the model’s learning process.

                                    Table 12. Results of key module ablation experiment.

                                      Model Configuration                  AA      AP      AR       F1       FM     BWT      IR      MR     Top-3
                                      Full Model                                    83.4      82.7     81.5     82.1      9.4    −2.9     0.91     63.2      17.1
                                      w/o Multi-Level Distillation     79.2     78.5     77.3     77.9     13.7   −4.3     0.84     59.6      20.4
                                      w/o DP-Means Memory            78.6     77.1     75.8     76.4     15.1   −4.5     0.79     55.2      22.8
                                      w/o Meta-weighting                   76.7     75.2     73.9     74.5     16.3   −4.8     0.71     52.4      24.9
                                      w/o Semi-Supervised                 74.9     73.4     72.1     72.7     17.4   −5.1     0.66     49.1      26.2
                                      w/o Pseudo-Labeling                 81.3     80.8     79.5     80.1     10.7   −3.2     0.89     62.8      18.3
                                    The bold font highlights the best performance in each metric.

                                    5. Limitations and Future Work
                                          Thispaperpresentsasystematicstudyondynamicintrusiondetectionbasedonthe
                                    integrationofSSLandCL,withaparticularfocusonthreecriticalchallengesinreal-world
                                    networksecurity: thecontinuousevolutionofattackpatterns,thescarcityoflabeleddata,
                                    and the imbalance in category distributions.  To address these issues, we propose the
                                    framework, which incorporates dynamic memory construction, multi-level knowledge
                                    alignment, and meta-learning-based class-aware optimization. Extensive experiments on
                                    multiplereal-worldintrusiondetectiondatasetsdemonstratethatourmethodsignificantly
                                    outperformsexistingstate-of-the-artmethodsacrosskeymetrics. Theseresultsvalidatethe
                                    practicality,stability,andgeneralizationcapacityoftheproposedapproachunderdynamic
                                    task sequences, label-deficient settings, and skewed data distributions.
                                          Despite the promising results, there are several limitations to our current approach
                                    that warrantfurther investigation. More detailedtheoretical analysis: While our empirical
                                    resultsarestrong,adeepertheoreticalunderstandingoftheconvergencepropertiesand
                                    generalizationboundsoftheproposedframeworkwouldprovidevaluableinsightsinto
                                    itsperformanceguarantees. Thepotentialofadversarialattacks: Asourmethodrelieson
                                    pseudo-labelingandmemoryreplay,itmaybevulnerabletoadversarialattacksthatexploit
                                    thesemechanisms. Futureworkshouldexplorerobusttrainingtechniquestomitigatesuch
                                    risks. More detailed experiments: Although we have conducted extensive experiments,
                                    further evaluationson largerand more diversedatasets, as well asreal-world deployment
                                    scenarios,wouldhelptobetterunderstandthepracticalapplicabilityandlimitationsofour
                                    approach. The results in extremely imbalanced scenarios still have room for improvement,
                                    and wewill continueto exploremoreeffective solutions. The results given byour method
                                    donotincludeeachintrusioncategory’sperformance,whichisalsoanimportantevaluation
                                    indicatorforintrusiondetectiontasks. Computationalefficiency: Theproposedframework
                                    involves multiple components that may introduce computational overhead. Future work
```


### PDF page 23

[View original page, figures and tables](assets/page-023.png)

```text
Future Internet2025,17, 456                                                                                                                      23 of 25



                                      should focuson optimizing theefficiency of the modelto ensureits feasibility forreal-time
                                      intrusion detection applications.
                                            Infuturework,weplantofurtherexplorethedirectionsintroducedbelow. Onlineand
                                      Real-Time Adaptation: Extend the current framework to support real-time data streams
                                      and online continual learning, enabling immediate response to emerging threats in live
                                      environments. ModelInterpretabilityandTransparency: Incorporateexplainablelearning
                                      mechanisms to enhance the interpretability of model predictions, making the system’s
                                      decision-making process more transparent, accountable, and trustworthy, which is crucial
                                      for security-critical applications.
                                            Theseenhancementsaimtobroadenthepracticaldeploymentscopeofourmethod
                                      andfurtherbridgethegapbetweentheoreticalmodelsandreal-worlddynamicintrusion
                                      detection systems.

                                      AuthorContributions: Methodology,software,validation, formalanalysis, investigation, resources,
                                      data curation, writing—original draft preparation, writing—review and editing, C.G.; writing—
                                      review and editing, X.L., J.C., S.Y., visualization, supervision, project administration, funding acquisi-
                                      tion, H.G. All authors have read and agreed to the published version of the manuscript.

                                      Funding: This research received no external funding.

                                      DataAvailabilityStatement: Thedatapresentedinthisstudyareavailableuponrequestfromthe
                                      author. The dataset can be accessed athttps://research.unsw.edu.au/projects/\{unsw-nb15-dataset,
                                      toniot-datasets\}(UNSW-NB15 and TON_IoT, accessedon 15 March 2025),https://www.unb.ca/
                                      cic/datasets/ids-2017.html(CIC-IDS2017, accessed on 1 April 2025).

                                      Acknowledgments: The authors would like to thank the anonymous reviewers for their valuable
                                      feedbackandsuggestions. Theauthorsalsothankthemembersoftheresearchgroupfortheirhelpful
                                      discussionsandsupportduringthedevelopmentofthiswork. Theauthorsalsothanktheeditorsfor
                                      theirassistanceinthepublicationprocessandformercolleaguesfortheircontributionstotheearly
                                      stages of this research.

                                      Conflicts of Interest:The authors declare no conflicts of interest.

References
1.      Du,L.;Gu,Z.;Wang,Y.;Wang,L.;Jia,Y. Afew-shotclass-incrementallearningmethodfornetworkintrusiondetection. IEEE
      Trans. Netw. Serv. Manag. 2023,21, 2389–2401. [CrossRef]
2.      VandeVen,G.M.;Tuytelaars,T.;Tolias,A.S. Threetypesofincrementallearning. Nat. Mach. Intell. 2022,4,1185–1197. [CrossRef]
3.   Nasteski, V. An overview of the supervised machine learning methods.    Horizons B2017, 4, 56. [CrossRef]
4.      Zhu, X.J. Semi-Supervised Learning Literature Survey: Technical Report; University of Wisconsin-Madison Department of Computer
      Sciences: Madison, WI, USA, 2005.
5.      Shyaa,M.A.;Zainol, Z.;Abdullah,R.;Anbar,M.;Alzubaidi,L.; Santamaría,J. Enhancedintrusiondetectionwithdata stream
      classification and concept drift guided by the incremental learning genetic programming combiner.   Sensors 2023, 23, 3736.
      [CrossRef] [PubMed]
6.      Alshamrani, A.; Myneni, S.; Chowdhary, A.; Huang, D.  A survey on advanced persistent threats:  Techniques, solutions,
      challenges, and research opportunities. IEEE Commun. Surv. Tutor. 2019,21, 1851–1877. [CrossRef]
7.      Bilge,L.; Dumitra¸s,T. Beforewe knewit: Anempiricalstudyof zero-dayattacksin thereal world. InProceedingsofthe2012
      ACM conference on Computer and Communications Security, Raleigh, NC, USA, 16–18 October 2012; pp. 833–844.
8.      Kirkpatrick, J.; Pascanu, R.; Rabinowitz, N.; Veness, J.; Desjardins, G.; Rusu, A.A.; Milan, K.; Quan, J.; Ramalho, T.; Grabska-
      Barwinska, A.; et al. Overcoming catastrophic forgetting in neural networks. Proc. Natl. Acad. Sci. USA 2017, 114, 3521–3526.
      [CrossRef] [PubMed]
9.      Baysal, E.; Bayılmı¸s, C. Overcoming Class Imbalance in Incremental Learning Using an Elastic Weight Consolidation-Assisted
      Common Encoder Approach. Mathematics2025,13, 1887. [CrossRef]
10.    Zenke, F.; Poole, B.; Ganguli, S. Continual learning through synaptic intelligence. In Proceedings of the International Conference
      on Machine Learning, PMLR, Sydney, NSW, Australia, 6–11 August 2017; pp. 3987–3995.
```


### PDF page 24

[View original page, figures and tables](assets/page-024.png)

```text
Future Internet2025,17, 456                                                                                                                           24 of 25



11.    Rebuffi, S.A.; Kolesnikov, A.; Sperl, G.; Lampert, C.H. icarl: Incremental classifier and representation learning. In Proceedings of
      the IEEE Conference on Computer Vision and Pattern Recognition, Honolulu, HI, USA, 21–26 July 2017; pp. 2001–2010.
12.    Prabhu,A.;Torr,P.H.;Dokania,P.K. Gdumb: Asimpleapproachthatquestionsourprogressincontinuallearning. InProceedings
      of the Computer Vision–ECCV 2020: 16th European Conference, Glasgow, UK, 23–28 August 2020; Proceedings, Part II 16;
      Springer: Berlin/Heidelberg, Germany, 2020, pp. 524–540.
13.    Bhurani, P.; Chouhan, S.S.; Mittal, N. Exbcil: An exemplar-basedclass incremental learningfor intrusiondetection system. Int. J.
      Mach. Learn. Cybern. 2025, 16, 3865–3885. [CrossRef]
14.    Xu, H.; Wang, Y. A continual few-shot learning method via meta-learning for intrusion detection. In Proceedings of the 2022
      IEEE 4th International Conference on Civil Aviation Safety and Information Technology (ICCASIT), Dali, China, 12–14 October
      2022; pp. 1188–1194.
15.    Wang, R.; Fei, J.; Zhang, R.; Guo, M.; Qi, Z.; Li, X. Drnet: Dynamic retraining for malicious traffic small-sample incremental
      learning. Electronics2023,12, 2668. [CrossRef]
16.    Sabeel,U.;Heydari,S.S.;El-Khatib,K.;Elgazzar,K. IncrementalAdversarialLearningforPolymorphicAttackDetection. IEEE
      Trans. Mach. Learn. Commun. Netw. 2024, 2, 869–887. [CrossRef]
17.Li, Z.; Hoiem, D. Learning without forgetting.      IEEE Trans. Pattern Anal. Mach. Intell. 2017,40, 2935–2947. [CrossRef]
18.    Douillard,A.;Cord,M.;Ollion,C.;Robert,T.;Valle,E. Podnet: Pooledoutputsdistillationforsmall-tasksincrementallearning.
      InProceedingsof theComputerVision—ECCV 2020: 16thEuropeanConference,Glasgow, UK,23–28August 2020;Proceedings,
      Part XX 16; Springer: Berlin/Heidelberg, Germany, 2020; pp. 86–102.
19.    Smith,J.;Balloch,J.;Hsu,Y.C.;Kira,Z. Memory-EfficientSemi-SupervisedContinualLearning: TheWorldisitsOwnReplay
      Buffer. InProceedingsofthe2021InternationalJointConferenceonNeuralNetworks(IJCNN),Shenzhen,China,18–22July2021;
      pp. 1–8. [CrossRef]
20.    Gao, J.; Chai, S.; Zhang, B.; Xia, Y. Research on network intrusion detection based on incremental extremelearning machine and
      adaptive principal component analysis. Energies2019,12, 1223. [CrossRef]
21.    Amalapuram, S.K.; Tamma, B.R.; Channappayya, S.S. Spider: A semi-supervised continual learning-based network intrusion
      detectionsystem. InProceedingsoftheIEEEINFOCOM2024—IEEEConferenceonComputerCommunications,Vancouver,BC,
      Canada, 20–23 May 2024; pp. 571–580.
22.    Abdallah, E.E.; Otoom, A.F.; Otoom, A.F. Intrusion detection systemsusing supervised machinelearning techniques: Asurvey.
      Procedia Comput. Sci. 2022,201, 205–212. [CrossRef]
23.    Chen, C.; Gong, Y.; Tian, Y. Semi-supervised learning methods for network intrusion detection. In Proceedings of the 2008 IEEE
      International Conference on Systems, Man and Cybernetics, Singapore, 12–15 October 2008; pp. 2603–2608.
24.    Sohn, K.; Berthelot, D.; Carlini, N.; Zhang, Z.; Zhang, H.; Raffel, C.A.; Cubuk, E.D.; Kurakin, A.; Li, C.L. Fixmatch: Simplifying
      semi-supervised learning with consistency and confidence. Adv. Neural Inf. Process. Syst. 2020,33, 596–608.
25.    Lee, D.H. Pseudo-label: The simple and efficient semi-supervised learning method for deep neural networks. In Proceedings of
      the Workshop on Challenges in Representation Learning, ICML, Atlanta, GA, USA, 16–21 June 2013; Volume 3, p. 896.
26.    Xie,Q.;Dai,Z.;Hovy,E.;Luong,T.;Le,Q. Unsuperviseddataaugmentationforconsistencytraining. Adv. NeuralInf. Process.
      Syst. 2020, 33, 6256–6268.
27.    Tarvainen, A.; Valpola, H. Mean teachers are better role models: Weight-averaged consistency targets improve semi-supervised
      deep learning results. Adv. Neural Inf. Process. Syst. 2017,30, 1195–1204.
28.    Berthelot, D.;Carlini, N.; Goodfellow, I.;Papernot, N.; Oliver, A.; Raffel,C.A. Mixmatch: A holistic approach to semi-supervised
      learning. Adv. Neural Inf. Process. Syst. 2019, 32, 5049–5059.
29.    Chen, T.; Kornblith, S.; Norouzi, M.; Hinton, G.  A simple framework for contrastive learning of visual representations.  In
      Proceedings of the International Conference on Machine Learning, PmLR, Online, 13–18 July 2020; pp. 1597–1607.
30.    Lechat, A.; Herbin, S.; Jurie, F. Pseudo-labeling for class incremental learning. In Proceedings of the BMVC 2021: The British
      Machine Vision Conference, Online, 22–25 November 2021.
31.    Cermelli,F.;Fontanel,D.;Tavera,A.; Ciccone,M.;Caputo,B. Incrementallearningin semanticsegmentationfromimagelabels.
      InProceedingsoftheIEEE/CVFConferenceonComputerVisionandPatternRecognition,NewOrleans,LA,USA,18–24June
      2022; pp. 4371–4381.
32.    Cui,Y.;Jia, M.;Lin,T.Y.; Song,Y.;Belongie,S. Class-balanced lossbasedon effective numberofsamples. In Proceedingsofthe
      IEEE/CVF Conference on Computer Vision and Pattern Recognition, Long Beach, CA, USA, 15–20 June 2019; pp. 9268–9277.
33.    Cao,K.;Wei,C.;Gaidon,A.;Arechiga,N.;Ma,T. Learningimbalanceddatasetswithlabel-distribution-awaremarginloss. Adv.
      Neural Inf. Process. Syst. 2019,32, 1567–1578.
34.    Moustafa, N.; Slay, J. UNSW-NB15: A comprehensive data set for network intrusion detection systems (UNSW-NB15 network
      dataset). In Proceedingsof the2015 MilitaryCommunications andInformation SystemsConference (MilCIS), Canberra,ACT,
      Australia, 10–12 November 2015; pp. 1–6.
```


### PDF page 25

[View original page, figures and tables](assets/page-025.png)

```text
Future Internet2025,17, 456                                                                                                                              25 of 25



35.    Sharafaldin, I.; Lashkari, A.H.; Ghorbani, A.A.  Toward generating a new intrusion detection dataset and intrusion traffic
      characterization. ICISSp 2018, 1, 108–116.
36.    Booij, T.M.; Chiscop, I.; Meeuwissen, E.; Moustafa, N.; Hartog, F.T.H.d.  ToN_IoT: The Role of Heterogeneity and the Need
      forStandardizationofFeaturesandAttackTypesinIoTNetworkIntrusionDataSets. IEEEInternetThingsJ.2022,9,485–496.
      [CrossRef]
37.    Koroniotis, N.; Moustafa, N.; Sitnikova,E.; Turnbull, B. Towards the development ofrealisticbotnet dataset inthe internet of
      things for network forensic analytics: Bot-iot dataset. Future Gener. Comput. Syst. 2019,100, 779–796. [CrossRef]
38.    Belouadah, E.; Popescu, A. Il2m: Class incremental learning with dual memory. In Proceedings of the IEEE/CVF International
      Conference on Computer Vision, Seoul, Republic of Korea, 27 October–2 November 2019; pp. 583–592.
39.    Lechat, A.; Herbin, S.; Jurie, F.  Semi-supervised class incremental learning.   In Proceedings of the 2020 25th International
      Conference on Pattern Recognition (ICPR), Milan, Italy, 10–15 January 2021; pp. 10383–10389.


Disclaimer/Publisher’s Note:The statements, opinions and data contained in all publications are solely those of the individual
author(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to
people or property resulting from any ideas, methods, instructions or products referred to in the content.
```
