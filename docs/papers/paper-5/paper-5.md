# Investigating the Impact of Label-flipping Attacks against Federated Learning for Collaborative Intrusion Detection

**Authors:** Léo Lavaur; Yann Busnel; Fabien Autrel

**Publication:** Computers & Security (2025).

**Publication DOI:** https://doi.org/10.1016/j.cose.2025.104462

**Verified free PDF:** https://orbilu.uni.lu/bitstream/10993/65906/1/Investigating_the_Impact_of_Label_flipping_Attacks_against_Federated_Learning_for_Collaborative_Intrusion_Detection.pdf

**Downloaded version:** University-repository author manuscript dated 29 September 2025, linked to the published Computers & Security article. Author version, not publisher typesetting.

**Qualification:** Q1, COMPUTER SCIENCE, INFORMATION SYSTEMS. Journal rankings use the 2024 JIF category quartile (June 2025 JCR), not an asserted 2026 ranking.

**Integrity:** 34 pages; 1,339,480 bytes; SHA-256 `bb8198732d4716fc25471120be67a9240eefcc58d6b3b3ad8bc945c97165c00d`. Verified 8 October 2026.

## Reading and extraction note

The PDF is the authoritative complete manuscript. Below is automatic page-level text extraction, not a newly authored summary or a verbatim-quality transcription. Two-column order, formulas, ligatures and table spacing can be imperfect. Every page has a rendered PNG in `assets/` for inspecting figures, equations and tables at their original locations. Publication metadata is saved alongside the images. The technical review is in [the selection audit](../phase2-selection-audit.md).

## Full manuscript text


### PDF page 1

[View original page, figures and tables](assets/page-001.png)

```text
Highlights

InvestigatingtheImpactofLabel-flippingAttacksagainstFederated
LearningforCollaborativeIntrusionDetection⋆
LéoLavaur,YannBusnel,FabienAutrel

   • Thefirstsystematicanalysisoftheimpactoflabel-flippingattackson
      CollaborativeIntrusionDetectionSystems(CIDSs)leveragingFederated
      Learning(FL),answeringasetofresearchquestions.

   • Acomprehensiveunderstandingoftheimpactoftheseattacksonthe
      performanceofthelearningalgorithm.

   • Areusablemethodologytoassesstheimpactoflabel-flippingattackson
      FL,withexperimentsthatcanbeeasilyreplicatedandextendedtoother
      datasets,attacktypes,andmitigationstrategies.

   • AnautomationframeworktofacilitatetheevaluationofFLapproaches
      underdifferentattackscenarios,builtuponFlowerandHydra.

   • Ademonstrationthatsimilarity-basedmitigationstrategieswillfalterin
      heterogeneoussettings.
```


### PDF page 2

[View original page, figures and tables](assets/page-002.png)

```text
InvestigatingtheImpactofLabel-flippingAttacksagainst
FederatedLearningforCollaborativeIntrusionDetection


                LéoLavaura,b,c,1,YannBusnelc,d,FabienAutrela,c

                            aIMT Atlantique, Rennes, France
     bInterdisciplinary Centre for Security, Reliability and Trust (SnT), University of
                                Luxembourg, Luxembourg
                        cIRISA (SOTERN team), Rennes, France
                       dInstitut Mines-Télécom, Palaiseau, France




Abstract
TherecentadvancesinFederatedLearning(FL)anditspromiseofprivacy-
preservinginformationsharinghaveledtoarenewedinterestinthedevelopment
ofcollaborativemodelsforIntrusionDetectionSystems(IDSs). However,its
distributednaturemakesFLvulnerabletomaliciouscontributionsfromitspar-
ticipants,includingdatapoisoningattacks. Label-flippingattacks—wherethe
labelsofasubsetofthetrainingdataareflipped—havebeenoverlookedinthe
contextofIDSsthatleverageFLprimitives. Thisworkcontributestoclosing
thisgapbyprovidingasystematicandcomprehensiveoverviewoftheimpact
oflabel-flippingattacksonFederatedIntrusionDetectionSystems(FIDSs).We
showthattheeffectsofsuchattackscanrangefromseveretohighlymitigated,
dependingonhyperparametersanddatasetcharacteristics,andthattheirmiti-
gationisnon-trivialinheterogeneoussettings.Wediscussthesefindingsinthe
contextofexistingliteratureandproposerecommendationsfortheevaluation
ofFIDSs.Finally,weprovideamethodologyandtoolstoextendourfindingsto
othermodelsanddatasets,thusenablingthecomparableevaluationofexisting
andfuturecountermeasures.
Keywords: federatedlearning,intrusiondetection,data-poisoning,
label-flipping,systematicanalysis,quantitativeassessment.





  ⋆ThisresearchwaspartlyfundedbythechairCyberCNI.frwithsupportoftheEuropean
UnionthroughtheEuropeanRegionalDevelopmentFund(ERDF)oftheBrittanyRegion
(EU001043).
   Email addresses:  leo.lavaur@uni.lu(LéoLavaur), yann.busnel@imt.fr(YannBusnel),
fabien.autrel@imt-atlantique.fr(FabienAutrel)
  1LéoLavaurwasoriginallywithIMTAtlantiqueandIRISA,buthassincejoinedtheSnT
atUniversityofLuxembourg









Preprint submitted to Computers & Security                                          September 29, 2025
```


### PDF page 3

[View original page, figures and tables](assets/page-003.png)

```text
1. Introduction

   Securinginformationsystemsisbecomingincreasinglydifficult,whetherdue
tothegrowingcomplexityofthesystemsthemselvesorthesophisticationofthe
attackstheyface.Intrusiondetectionsystemsareacriticalcomponentofthese-
curityinfrastructureofanyorganization,offeringcomplementarydefensemech-
anismstotraditionalpreventivemeasures.Inthiscontext,FederatedLearning
(FL)hasemergedasapromisingapproachtobuildcollaborativeIntrusionDe-
tectionSystems(IDSs)thatcanleveragethecollectiveknowledgeofmultiple
organizationswithoutcompromisingtheconfidentialityoftheirdata[1].Since
2018,numerousworkshaveexperimentedwithvariousapplicationsofFeder-
atedIntrusionDetectionSystem(FIDS),suchasInternetofThings(IoT)[2]
orVehicle-to-Everything(V2X)[3].MultiplesurveysonFLforIDSshavealso
beenpublished,highlightingthecommunity’sinterest[4–9].
   However,thedistributednatureofthistypeofcollaborativesystemintro-
ducesnewattackvectors,notablyrelatedtothequalityofthecontributions.
Amongthechallengesidentifiedintheliterature,therobustnessofFLtopoison-
ingattackshasbeenarecurringconcern[10,11]. Thesechallengesarefurther
exacerbatedinthecontextofIDSs,wheretheperformanceofthelearningal-
gorithmdirectlyimpactsthesecurityofthemonitoredsystem.
   Whileasignificantamountofliteratureexistonmitigationstrategiesagainst
poisoningattacksinFIDSs,fewstudiesfocusonunderstandingandquantifying
theimpactoftheseattacks.Inaddition,mostexistingwork,eitherinthecon-
textofFIDSsormoregenerallyinFL,focusesoncross-devicefederations,which
arelessrepresentativeofthiscollaborativesetting.Inparticular,theeffectsof
label-flippingattacksremainedoverlooked. Tothebestofourknowledge,no
systematicstudyhasbeenconductedtounderstandtheirimpactonFLforCol-
laborativeIntrusionDetectionSystems(CIDSs),andthelackofcomparability
intheexistingliteraturemakesitdifficulttogeneralizethepublishedfindings.
   Thispaperthusaimstofillthesegapsbyfurtherinvestigatinglabel-flipping
attacksinFIDSs,andunderstandingtheconditionsunderwhichtheseattacks
aremosteffective. Wedosobyconductingasystematicandquantitativeas-
sessmentoftheimpactoflabel-flippingattacksonFIDSs.Theseattackspresent
apparentsimplicity,astheyonlyimplychangingthelabelsofasubsetofthe
trainingdata.Forattackers,theyareconsequentlyrelativelyeasytoimplement,
eveninablack-boxed system. However,suchbasicmanipulationscanhavea
significantimpactonthetrainedglobalmodel.
   Specifically,thisstudyaimstoanswerthefollowingresearchquestions.

RQ1. Isthebehaviorofpoisoningattackspredictable?
RQ2. Dohyperparametersinfluencetheimpactofpoisoningattacks?

RQ3. AreIDSbackdoorsrealisticusinglabel-flippingattacks?

RQ4. Isthereacriticalthresholdwherelabel-flippingattacksbegintoimpact
       performance?


                                         2
```


### PDF page 4

[View original page, figures and tables](assets/page-004.png)

```text
RQ5. Areexistingtechniqueswell-suitedtodetectlabel-flippingattacks?

   Insummary,thecontributionsofthisworkarefivefold:

   • the first systematic analysis ofthe impact of label-flipping attacks on
      CIDSsleveragingFL;
   • Acomprehensiveunderstandingoftheimpactoftheseattacksonthe
      performanceofthelearningalgorithm;

   • AreusablemethodologytoassesstheimpactofpoisoningattacksonFL,
      with experiments that can be easily replicated and extended to other
      datasets,attacktypes,andmitigationstrategies;

   • AnautomationframeworktofacilitatetheevaluationofFLapproaches
      underdifferentattackscenarios,builtuponFlower[12]andHydra[13].
   • Ademonstrationthatsimilarity-basedmitigationstrategieswillfalterin
      heterogeneoussettings

   Thecontentofthisarticlebuildsuponourworkpreviouslypublishedatthe
InternationalConferenceonAvailability,ReliabilityandSecurity(ARES)[14].
Itsremainderisorganizedasfollows. First,Section2presentsthenecessary
backgroundinformationonFLandpoisoningattacksinthiscontext.Section3
detailsrelatedworks,notablytheexistinganalysesontheimpactofpoisoning
attacksonFL.InSection4,wediscussthemethodologyusedtocarryoutthe
experiments,withanemphasisonreproducibility.Then,Section5presentsthe
resultsoftheexperiments,answeringtheresearchquestions.Finally,Section6
discussestheimplicationsofourfindingsandthelimitationsofthisstudy.We
concludeinSection7bysummarizingthemaintakeawaysanddiscussingfuture
workthatcouldbeconductedtoextendthisstudy.

2. Preliminaries

2.1. FederatedLearningforIntrusionDetection
   FLisadistributedlearningparadigmthatenablestrainingaglobalmodel
withoutsharinglocaldata[1].Modeltrainingisstructuredinrounds,wherean
orchestratingserver Srandomlytasks nparticipants pi,i∈ J1,nKfromapool
ofparticipants P totrainamodel wri ateachround r. Theroundendswith
theaggregationofthecollectedmodelsintoanewglobalmodel Wr,whichis
redistributedtotheclientsasastartingpointforthenextround(r+1). De-
pendingonthescaleofthefederation—i.e.,cross-siloorcross-device[15]—,the
fraction Cofselectedparticipantsperroundcanvary.Themodelarchitecture
andhyperparametersarethesameacrossthefederation,buteachparticipant
ownsalocaldataset dithatisnotsharedwiththeothers.
   InthecontextofIDSs,participantsgenerallyseektoclassifynetworkflows
intotwoclasses(benignandmalicious),whichisabinaryclassificationtask.
Consequently,eachdataset diisasetofdatapointsrepresentingflows,andit


                                         3
```


### PDF page 5

[View original page, figures and tables](assets/page-005.png)

```text
associateseachflow ⃗xjwithitslabel ⃗yj. Werefertotheelementsofadataset
assamples.Thedistributionofeachdataset didependsonthecollectedtraffic,
andthereforevariesdependingonthedevicesorservicesactiveonthenetwork.
Variousdegreesofsimilaritybetweenclientsexist, frompurelyIndependent
andIdenticallyDistributed(IID)partitioningtopathological non-IID(NIID)
settings, whereallclientshaveuniquedata-distributionswithoutclassover-
lap[16].
   Totraintheirmodel,theparticipantsaimatminimizingalossfunction

                             L(w, ⃗xj,yj),j∈ J1,|di|K,                     (1)

where ⃗xjand yjarethesampleanditslabel,respectively. Todoso,theyuse
anoptimizerleveragingtheprinciplesofStochasticGradientDescent(SGD).
Aftercomputingthegradients∇L(w, ⃗xj,yj),theyupdatetheirmodelas

                            wr+1i    ←w−η∇L(wi,di),                    (2)

where ηisthelearningrate. Alternatively,theyuploadthegradientstothe
server,whichwillupdatetheglobalmodel Wrasafunctionofthegradients
{∇L(wi,di)|i∈ J1,nK}(e.g., FedSGD[1]).Whetherthemodelisupdatedlocally
orglobally,theserveraggregatestheuploadedparametersandbroadcaststhe
newglobalmodeltotheparticipants.
   Thedefinitivechoiceoftheaggregationmethoddependsonthelearning
objective,butalsoontheassumeddatadistributionbetweentheparticipants.
Theoriginalpathological-NIIDsettings[1]israrelyencounteredinpractice,as
abinary-classificationtasktypicallyrequiresbothbenignandmaliciousdata.
Consequently,theliteratureoftenreliesononeoftwostrategies[17]:(a)dis-
tributingadatasetamongclientsandthenremovingsamplesfrom nattack
classesfromeach;or(b)distributingthebenigndataamongclientsandthen
assigningsamplesfrom nattackclassestoeachclient,withorwithoutclass
overlap.Camposetal.[9]alsoexaminealternativepartitioningstrategiesthat
aredeemedmorerealistic,suchasseparatingdatabyIPaddresses. Notethat
thisdoesnotaccountforresourceornetworkheterogeneity,whicharelessrel-
evantinaninter-organization, cross-silofederation. However, theliterature
hasshowntheirimportanceincross-devicesettings,wherestragglersandslow
networkscansignificantlyaffectthetrainingprocess[15].

2.2. PoisoningAttacksinFederatedLearning
   TheattacksurfaceofFLisratherbroad,asitincludesvarioustypesof
threats, suchaspoisoningandprivacyattacks[18]. Authorsoftenreferto
poisoningattacksinFLasByzantineattacks,sincetheyareanalogoustothe
ByzantineGeneralproblem[19]indistributedsystems.Likewise,thetermSybil
attacks[20]isfrequentlyusedtorefertotheproblemofcolludingattackers[21].
   Poisoningattackscanbeclassifiedintotwomaincategoriesdependingonthe
phaseinwhichtheyareperpetrated:model-poisoning[10]ordata-poisoning[11].
Model-poisoningattacksaimatmanipulatingthemodelparameters,usually


                                          4
```


### PDF page 6

[View original page, figures and tables](assets/page-006.png)

```text
duringoraftertraining,todeviatetheaggregatedmodelfromtheglobalopti-
mum[22].Data-poisoningattacks,ontheotherhand,occurbeforethetraining
phaseandmanipulatedatasamplestodegradeperformance,causemisclassifi-
cation,orintroducebackdoors[18].
   Datapoisoningattackscanbecategorizedintoclean-labelandlabel-flipping
attacks. Clean-labelattacksmanipulatethesamplestobemisclassified,either
byaddingnewsamples[23]orbymodifyingexistingones[24]. Label-flipping
attacks,ontheotherhand,changethelabelsofthesamplesbyflippingthem
toadifferentclass[11].
   Inaddition,mostpoisoningattackscanbefurtherseparatedintountargeted
andtargeted attacks. Untargetedattacksrandomlyselectsamplestobema-
nipulatedandareusuallyeasiertodetectastheyhaveahigherimpactonthe
model’sperformance.Targetedattacks,ontheotherhand,selectsamplesbased
onaspecificcriterion,suchastheclasstobetargeted.InaCIDScontext,tar-
getedattackscanbeusedtointroducebackdoors—i.e.,makingaspecificattack
classbemisclassifiedasbenign—orcausetargetedmisclassification.

2.3. Countermeasures
   Algorithmicsolutionsexisttomitigatethesethreatsbyusingmorerobust
aggregationstrategies.ThisincludesKrum[25],whichelectsthemodelupdate
thatisclosesttotheothersasthenewglobalmodel,orTrimmedMean[26],
whichaggregatesthemodelupdatesbytrimmingthehighestandlowestvalues.
Bothmethodssharethegoaloffilteringoutoutliers,assumingthattheywould
negativelyimpacttheglobalmodel.
   Thisnotionofdistancebetweenupdatesisoftenleveragedtodifferentex-
tentsintheliterature.Clustering-basedmethods[27,28]groupsimilarupdates
together,eithertoeliminateoutliersortoidentifyclustersofupdatesthatmay
beindicativeofanattack.Similarly,othersimilarity-analysistechniques[21,29]
usethedistancebetweenupdatestoflagparticipantsthatmightbesuspiciously
similar.
   Althoughotherlessconventionalmethodsexist,suchasclient-sideevalua-
tion[30,31],theyareoftenmorecomputationallyexpensiveandlessscalable.
Moregenerally,thetrade-offbetweencomputationaloverheadandrobustness
isarecurringthemeintheliterature,andthedesignofacountermeasureoften
dependsonthespecificthreatmodelandrequiresadeepunderstandingofthe
attackcapabilities.


3. RelatedWork

   TheliteratureontheimpactofpoisoningattacksonFL[10,11,32,33]pro-
videsinsightintothebehaviorofpoisoningattacksongenericMachineLearning
(ML)tasks,suchasimageclassificationornaturallanguageprocessing.Nuding
andMayer[32]focusspecificallyonbackdoorattacks,andemphasizetheimpor-
tanceofthechoiceofthetriggerpattern.Fangetal.[22],Sunetal.[33]rather
studymodel-poisoningattacks.Whileoftenmoreeffectivethandata-poisoning


                                         5
```


### PDF page 7

[View original page, figures and tables](assets/page-007.png)

```text
attacks,model-poisoningattacksaremorecomplextoimplement,astheyre-
quireaccesstotheuploadedmodelsandknowledgeoftheirfunctioning. The
workofTolpeginetal.[11]isclosesttoours,asitfocusesonlyonlabel-flipping
attacks. Amongthemostnotableoutcomes,theauthorsexhibitthattargeted
attacksareespeciallyeffective,havingsmalltonoimpactoutsidethetargeted
class. Wereviewnotablyreviewtheapplicabilityoftheseconclusionstothe
contextofIDSsinSection5.3.
   InthecontextofIDSs,theliteratureontheimpactofpoisoningattackson
FLisscarcer.Zhangetal.[23]provideasystematicanalysisofclean-labeldata-
poisoningattacks,wheretheyuseGenerativeAdversarialNetworkss(GANs)to
generatepoisonedsamples. Otherworksdiscussclean-labelattackstoalesser
extent[34,35].Theseworksofferacomplementaryviewtoourstudy,although
thelackofcomparabilityofthedatasetsandmodelsusedmakesitdifficultto
drawdirectcomparisons.
   Meanwhile, Merzouketal.[24]provideacomprehensiveanalysisonML
backdoorsinFLforIDSs. MLbackdoorsworkbymanipulatingsamplesto
associateaspecifictriggerpatternwithagivenclasssothatthemodelmis-
classifiessamplescontainingthetriggerpattern.Wecompareitsefficiencywith
label-flippingattacksinSection5.3.Finally,Yangetal.[36]discussthespecific
aspectsoflabel-flippingattacksinthecontextofFLforIDSs,usingtwodifferent
datasets,NSL-KDD[37]andUNSW-NB15[38].However,theyonlyimplement
label-flippingasarandomselectionofmalicioussamplestobeflipped,which
makestheresultslesscomparable.

4. Methodology
   Assessingtheimpactofdata-poisoningoverFLimpliesreviewingacon-
sequentamountofparametersandconfigurations. Tooptimizeourworkand
makeiteasilyreproducible,theresultspresentedinSection5havebeengen-
eratedusingapurposelydesignedevaluationframeworkbasedonFlower[12]
andHydra[13].WefollowtheACMguidelinesandterminology[39],andtake
measurestoensurethereusability ofourartifacts,thereproducibility ofour
results,andthereplicabilityofourexperiments.Specifically:
  1.Weprovidethemethodologyandallparametersnecessarytoreimplement
      andreplicatetheexperiments;
  2.DependenciesarepinnedusingPoetryforPythonandNixforsystem,
      allowingtheentiresoftwarepipelinetobeexecutedinthesameconditions;
  3.Allexperimentsareseededwherepossible,whichmakestheresultsrepro-
      duciblewithinathreedecimalprecision2;
  4.Theresultsandthecodetogeneratethemareavailableinopenaccess   3,



  2ThedistributednatureofFLmakesitdifficulttoensurethecompletereproducibilityof
theresults.
  3https://github.com/leolavaur/comsec_2024


                                         6
```


### PDF page 8

[View original page, figures and tables](assets/page-008.png)

```text
Table1:ClassdistributionofCIC-CSE-IDS2018(left)andUNSW-NB15(right)[40,41].


     Class               Sampled        Full             Class               Sampled       Full
  Benign                        880,623     16,635,567Benign                          960,078     2,295,222
  Malicious                    119,377       2,258,141Malicious                        39,922         95,053
  · DDoS                            73,558       1,390,270· Exploits                        13,187         31,551
  · DoS                              25,574         483,999· Fuzzers                           9,377         22,310
  · Bot                                7,595         143,097· Generic                           6,976         16,560
  · Brute  Force                    6,525         123,982· Reconnaissance                 5,352         12,779
  · Infiltration                  6,108         116,361· DoS                                 2,455           5,794
  · Injection                           17                432· Analysis                             969           2,299
                                                     · Backdoor                             925           2,169
                                                     · Shellcode                           617           1,427
                                                     · Worms                                   64              164
  Total                       1,000,000     18,893,708Total                         1,000,000     2,390,275


       asarethedatasets4.

    Theresultspresentedinthispaperamountto10670uniqueruns,andclose
to1613cumulatedcomputinghoursontwoNixOSserverswith96cores,768GB
ofRAMand2NvidiaTeslaT4each.

4.1. DatasetandPre-processing
    Duetothescaleoftherequiredexperiments,werequiredatasetsthatare
bothrepresentativeoftheproblemandsmallenoughtobeprocessedinarea-
sonableamountoftime. RecentworksonFLandIDS[42]proposedastan-
dardizedfeatureset(NF-V2)makingcross-datasetFLsetupseasier,whichuses
nProbe[43]anditsNetFlowV9formattoextractfeatures.Theauthorsnotably
provideconvertedversionsofknowndatasets,includingCSE-CIC-IDS2018[44]
andUNSW-NB15[38],thetwomostusedgenericNetwork-basedIntrusionDe-
tectionSystem(NIDS)datasetsintheliterature. UNSW-NB15isadataset
generatedusingtheIXIAPerfectStormtooltosimulatearealnetworkenviron-
mentandcontains9attackclasses:Analysis,Backdoor,DoS,Exploits,Fuzzers,
Generic,Reconnaissance,Shellcode,andWorms.CSE-CIC-IDS2018isalarger
scaleversionoftheCIC-IDS2017[44]dataset,generatedusingAWS.Itcontains
14attackslabelsgroupedin6classes:DDoS,DoS,Bot,BruteForce,Infiltration,
andInjection.
    Weusethe“sampled”versionofthedatasetsprovidedbytheauthors[41],to
makeourexperimentsmoremanageable. Table1summarizesthedistribution
oftheclassesinthedatasets. Afterpreprocessing,weevenlysplitthedataset
fortheexperiments,ensuringthesameclassdistributioninthetrainingand
testingsets. 80%ofthedatasetisusedfortraining,and20%fortesting. We
purposelydonotuseapropervalidationset, asthegoalistomeasurethe
performancedeltarelatedtotheimpactoftheattacksontheglobalmodel,and
nottooptimizethemodel’shyperparameters.Indeed,theparametersarekept
constantthroughouttheexperiments,asdetailedinTable2. Wesometimes




   4https://staff.itee.uq.edu.au/marius/NIDS_datasets/


                                                  7
```


### PDF page 9

[View original page, figures and tables](assets/page-009.png)

```text
(a) CIC-CSE-IDS2018                               (b) UNSW-NB15

Figure1:Cross-projectionsofthemalicioustrafficfromthetwodatasetsin2DusingPrincipal
ComponentAnalysis(PCA).Ontop,theframeofreferenceiscomputedusingthe sampled
dataset,andonthebottomthe fulldataset. The sampleddatasetisthenprojectedonthe
left,the fulldatasetontheright.


refertothedatasetsas cicidsand nb15forbrevityintheremainingofthis
paper.
   Toassesstherepresentativityofthedatasetssampling,wecomparethepro-
jectionsintwodimensionsofthetwodatasetsusingPCA.Figure1presents
cross-projectionsresults,dependingonthedatasetsusedtogeneratethepro-
jectionframe.Thereareconsequentoverlapsbetweentheclassesinthisprojec-
tion,implyingthateither2dimensionsarenotenoughtoseparatetheclasses,
ortherearefeaturesthatarenotrelevanttotheclassificationtask.Yet,thepro-
jectedpatternsareidenticalbetweenthetwodatasets,whichindicatesthatthe
samplingprocessdoesnotintroducesignificantdistributionbiasinthedataset.
Therefore,theexperimentsperformedonthesampleddatasetsshouldberep-
resentativeoftheobservedbehaviorsintheoriginaldataset.

4.2. LocalandFederatedTraining
   WeuseasimpleMultilayerPerceptron(MLP)modelwithtwohiddenlayers,
asimplementedbyPopoolaetal.[45]whousethesamedatasets;asummary
ofthemodel’sparametersisavailableinTable2.Trainedcentrally,thismodel
reachesanF1-scoreof0.966andanaccuracyof0.992onoursampledCIC-CSE-
IDS2018,and0.945and0.995ontheUNSW-NB15dataset,respectively.These
valuescanbeconsideredasbaselinesfortheFLexperiments.
   Wefocusontheimpactofdata-poisoningspecifically,andthereforeomit
otherfactorsthatcouldhurttheperformanceofthemodel,suchasclienthet-
erogeneityordisconnections. Wealsospecificallyconcentrateoureffortsona
collaborativecross-silosetting,whereallclientsareavailableateachroundand
C = 1.Insuchsetting,scalabilityislessofaconcern,butthequalityofthepar-
ticipants’datacannotbeguaranteed. Consequently,thedatasetispartitioned


                                          8
```


### PDF page 10

[View original page, figures and tables](assets/page-010.png)

```text
Table2:Learninghyperparameters.

                     Hyperparameter         Value
                   Learning rate                     0.0001
                   Hidden layers activation     ReLU
                   Output layer activation      Sigmoid
                   Input shape                        49
                   Number of hidden layers    2
                   Size of the hidden layers    128
                   Optimizer                           Adam
                   Loss function                     Binary cross-entropy
                   Aggregation                            FedAvg


into10IIDshardsof80,000datapoints,andeachclientisassignedwithone
shard.Ontheserver,theuploadedmodelsareaggregatedusing FedAvg—which,
sincethelocaldatasetsareofsimilarsizes,isequivalenttoasimpleaverageof
theweights.

4.3. AttackModelandImplementation
   Weconsiderdata-poisoningattackswheremaliciousparticipantscanalter
theirlocaldatasetsbeforetraining. Thisdefinitioncoversboth,participants
thathavebeencompromisedandthosethataredeliberatelymodifyingtheir
data. Further,thisscenariowillalwaysbeavailable,evenwithasecureand
immutableFLclientsoftware.Specifically,weimplementdata-poisoningusing
label-flippingattacks,wheretheattackerchangesthelabel yofasampletoa
newlabel yp;i.e., yp =¬yinabinary-classificationproblem.

Attacker’sObjective.Weconsidertwotypesofobjectivesfortheattackerde-
pendingonthetypeofattackleveraged. Withtargeted attacks,theattacker
aimstomakeaspecificattackpatternundetectable,andthereforeactasaback-
doorintheIDS.Thisisimplementedbylabelingarandomlyselectedfraction
ofaspecificattackclass(e.g.,DDoS)asbenign. Withuntargetedattacks,on
theotherhand,hisgoalistoproducehigh=FalsePositivesRate(FPR)and
FalseNegativeRate(FNR),whichcanoverwhelmthehumanoperatorsinvesti-
gatingthealerts.Here,arandomfractionoftheentiredatasetisaltered,where
thelabelofeachsampleisflippedfrombenigntoattackandviceversa. The
proportionofsamplesthatarealterediscontrolledbytheDataPoisoningRate
(DPR),whichistheratioofsamplesmatchingthetargetthatarealteredby
eachattackeronaspecificround. WenotetheDPR,orlocalpoisoningrate,
as α.

Attacker’sKnowledgeandCapabilities.Weconsiderattackerstobegray-box
adversaries,i.e.,theyhavethesameknowledgeasbenignclients,butareunable
tomodifythesystem’sbehavior,neitherlocallynorontheserver.Further,we
considerthatmultipleattackerscanbepresentinthesystem,andthattheycan
actinconcert. Thisscenarioisreferredtoascolludingattackers. Inthiscase,


                                           9
```


### PDF page 11

[View original page, figures and tables](assets/page-011.png)

```text
Table3:Experimentalparameters.Defaultparametersarehighlightedinboldandareused
ifnotspecifiedotherwise. Astargetsaredataset-specific,theavailabletargetsarelistedfor
eachdataset.

 Parameter     Values

 dataset                     cicids,  nb15
 batch_size               32,  128,  512
 epochs                       100_10x10,  100_4x25,  100_1x100,  300_10x30,  300_4x75,
                      300_1x300
 distribution           10-0,  9-1,  7-3,  5-5,  3-7
 scenario                   continuous-{10,30,60,70,80,90,95,99},  continuous-100,
                      late-3,  redemption-3
 target  (cicids)     untargeted,  bot,  dos,  ddos,  bruteforce,  infiltration,
                      injection
 target  (nb15)         untargeted,  generic,  analysis,  worms,  backdoor,  exploits,
                      untargeted,  shellcode,  dos,  reconnaissance,  fuzzers
 partitioner             iid_drop_1,  iid_drop_2,  iid_full,  iid_keep_1,
                      kmeans_drop_1,  kmeans_drop_2,  kmeans_full,  kmeans_keep_1
 seed                           1313,  1977,  327,  5555,  501,  421,  3263827,  2187,  1138,  6567


theattackerssharethesametargetandDPR.Theproportionofattackerscan
varyfromonesinglemaliciousclienttoamajorityofthembeingmalicious,and
isexpressedasτ,orModelPoisoningRate(MPR)[24].Notethatinthecontext
ofIIDpartitioning,theoverallpoisoningratecouldberegardedas α×τ.This
simplificationishowevernotaccurateinotherpartitioningstrategies.

4.4. Experiments
    Wedesignasetofexperimentstoanswertheresearchquestionsoutlined
inSection1.Allexperimentsshareacommonsetofconstantswhicharecom-
plementedbyasetofvariableparameters. Table3summariestheparameters
availablefortheexperiments.Eachcombinationistested10timesusingasetof
10differentseedstostudythepredictabilityoftheresults.Specifically,theseed
impactsdata-partitioningoperations(bothbetweentrainingandtestingsets
andbetweenclientsafterward),sampleselectioninpoisoningattacks,andthe
randomweightsoftheinitialmodel.Italsoimpactsalltherandomoperations
(suchasdatashuffling)performedduringmodeltraining.
    The epochsparametercontrolstheaggregationfrequency,i.e.,thenumber
oflocalepochsperround E,aswellasthenumberofrounds R. Logically,
batch_sizecontrolsthesizeofthebatchesusedateachiterationduringtrain-
ing. Theglobalnumberoflocalepochsperclientiskeptto100or300to
preservecomparability. The distributionrepresentsthenumberoflegitimate
andmaliciousclientsinthesystem,andconsequentlytheproportionofattack-
ers. Thekey scenariorepresentsthebehavioroftheattackers. Thescenarios
definedas continuous-αrepresentaconstantpoisoningrateof αthroughout
thetrainingprocess. Thescenariosnamed late-rand redemption-rproduce
anattackwith α = 100thatstartsorendsatround r,respectively.The target


                                            10
```


### PDF page 12

[View original page, figures and tables](assets/page-012.png)

```text
(a) CIC-CSE-IDS2018                            (b) UNSW-NB15

        Figure2:Impactofthepartitioningstrategyonthemodel’sperformance.


parameterrepresentsthetargetoftheattackasdefinedinSection4.3;each
attackclassisavailableasatarget.

4.4.1. PartitioningStrategies
   Aparticularparameterinthisselectionisthe partitioner,whichdefines
thestrategyusedtopartitionthedatasetamongtheclients. Asmentionedin
Section2.1,theliteratureofFIDSsusuallyconsiderseitherIIDpartitioning
orbasicNIIDscenarioswhereclientsrandomlydropattackclasses. Tostudy
theusageofsimilaritymetricstodetectpoisoningattacks,weconsidereight
differentpartitioningstrategies,withdifferentlevelsofheterogeneitythatrange
fromIIDpartitioningtopathological5settingswithoutdistributionoverlap.
   The partitionersmarkednamed iid_*distributethedatainanIIDman-
ner,whereeachclientreceivesastratified6subsetofthedataset. Then, full,
drop_*,and keep_*refertothewaytheattackclassesareprocessed: allkept,
certainclassesdropped,orcertainclasseskept,respectively.Thekmeans_*parti-
tionersuseak-meansclusteringalgorithmtopartitionthebenigntrafficamong
theclients,andthendistributetheattackclassesbasedontheirattribute(full,
drop_*, keep_*). Because k-meansalgorithmminimizestheintra-clustervari-
ance,itincreasestheheterogeneityoftheclients’datasets.Figure2illustrates
theperformanceofthemodelunderdifferentpartitioningstrategies.

4.5. Metrics
   Toquantifyhowtheexperimentparametersimpacttheglobalmodel,we
defineasetofmetricstomeasuretheAttackSuccessRate(ASR)ofpoisoning
attacks. ThedefinitionoftheASRdiffersdependingonthetypeofattack,
accordingtotheattacker’sobjectivedefinedinSection4.3. BecauseASRis
basedonperformanceandthereisnoperfectmodel,wedistinguishtheAbsolute
AttackSuccessRate(AASR)measuredintheattackscenario,fromtheRelative




  5In pathologicalNIIDsettings,eachclientownsauniqueclasswithoutanyoverlapwith
theothers.NotethatthesesettingsareparticularlyunrealisticforIDSpurposes.
  6Stratifiedsamplingensuresthattheclassdistributionremainsthesameamongthedif-
ferentshards. Itisusuallydoneusingthelabelsofthesamples,butanycategoricalfeature
canbeused.


                                          11
```


### PDF page 13

[View original page, figures and tables](assets/page-013.png)

```text
AttackSuccessRate(RASR)whichalsoconsidersthenominalperformance
withoutattacks.Formally,theRASRisdefinedas:

           RASR = max(AASRbenign,AASRattack)−AASRbenign1−AASRbenign                       ,       (3)

   whereAASRbenignandAASRattackaretheAASRofthebenignandattack
scenariosrespectively,underthesamesetofparameters.Thisismadepossible
thankstotheframework’sreproducibility,whichensuresthattwoexperiments
startedwiththesameseedwillrununderthesameconditions. Followingthe
definitionsinSection4.3,wethendefinedtwovariationsoftheAASRdepending
ontheattacker’sobjective.Botharecomputedbasedontheconfusionmatrix
ofthemodel:TruePositive(TP),TrueNegative(TN),FalsePositive(FP),and
FalseNegative(FN).

Targetedattacks: Maliciousparticipantsleveragetargetedattackstomakea
      specificattackpatternundetectable.Therefore,asuccessfulattackforces
      classificationoftherelevantattacksamplesasbenign.TheAASRisthen
      definedasthemissrateofthetargetedattack,i.e.


                                 AASR =   FNcTPc+FNc,                   (4)

      where cisaspecificattackclassofthedataset.
UntargetedAttacks: Untargetedattacksaimatdegradingtheoverallclassifica-
      tionrateofthemodel. Consequently,theAASRisdefinedasthemiss-
      classificationrateofthemodel,i.e.


                   AASR =      FP+FNTP+TN+FP+FN = 1−Accuracy.        (5)

   Additionally,weusetraditionalbinaryclassificationmetricstoobservethe
performanceofthemodelundervariousconditions, asidentifiedinexisting
surveys[5,9]Thesemetricsincludeaccuracy,F1-score,andmissrate.Notably,
weconsidertheMainTaskAccuracy(MTA),definedastheaccuracyofthe
benignclientsobtainedonthetestingset,tomeasuretheimpactoftheattacks
onthemodel’snominalperformance. Allmetricsareaggregatedoverthe10
runsofeachexperimentandthemeanandstandarddeviationarereportedfor
theselectedmetric.

5. Results

   Theresultspresentedinthissectionaimtoanswertheresearchquestions
definedinSection1. Figure3presentstheperformanceoftheglobalmodel
withoutmaliciousparticipantstoserveasacomparisonbaseline. Themodel
displaysrelativelyhighperformanceonbothdatasets,i.e.,above0.9foraccu-
racy,recall,andF1-score.However,someclassesaremorechallengingtodetect


                                        12
```


### PDF page 14

[View original page, figures and tables](assets/page-014.png)

```text
(a) CIC-CSE-IDS2018.                                 (b) UNSW-NB15.

Figure3: Baselineperformanceoftheglobalmodelwithoutmaliciousparticipants. The
accuracy,F1-score,andrecallillustratetheperformancethatcanbeexpectedfromtheglobal
modelundertheconditionsselectedforthisstudy(E  =  10, β  =  512). Therecallofthe
availableattackclassesshallserveasareferencefortheRASRoftargetedattacks.

                         Table4:ExperimentparametersforRQ1

 Isthebehaviorofpoisoningattackspredictable?

 batch_size                 32,  512
 epochs                         300_10x30,  300_4x75,  300_1x300
 distribution             5-5
 dataset                       cicids,  nb15


thanothers. Thelowrepresentationofthe“Injection”classincicids(around
0.0017%,seeTable1)preventsthemodelfromlearningfromit,whichresults
innosignificantimprovementovertime(seeFigure3a).The“Infiltration”class
ismorerepresentedinthedataset(0.6108%,approximatelythesameasthe
“BruteForce”and“Bot”classes),butremainsdifficulttolearnduetoitsappar-
entsimilaritytobenigntraffic. Consequently,itneverexceedsarecallof0.2.
Thedetectionin nb15isbetteroverall,withtheexceptionofthe“Analysis”and
“DoS”classesthatscorebelow0.9,althoughtheyarenottheleastrepresented
classesinthedataset.

5.1. ImpactPredictability
   Apreliminaryquestiontoanswerbeforequantifyingtheeffectsoflabel-
flippingiswhetherthebehaviorofpoisoningattacksispredictable. Thisis


                                            13
```


### PDF page 15

[View original page, figures and tables](assets/page-015.png)

```text
Figure4: Impactofthedatasetontheaccuracyunderpoisoning.  τ  = 0.5,E  = 10. The
x-axisrepresentsthenumberoflocalepochs.Eachlinerepresentstheaccuracyovertimefor
aspecificseed.Theseed6567on nb15(β = 512)isdepictedinred.


arequirementforgeneralizingourresultstootherdatasetsandmodels,and
comparingthefindingswithcurrentandfuturestudies. Duetocomputation
constraints,wefocusinthispartontheparametersthathavethemostsignifi-
cantimpactontheresults,asweneedtoperformlongerexperimentstoensure
thestabilityoftheresults. Specifically,theselecteddistributioncontains50%
ofmaliciousparticipants(i.e., τ = 0.5),whichroughlyequatesto50%ofthe
trainingdatabeingpoisoned.Theexperimentsarecarriedoutover300epochs,
withthreedifferentaggregationfrequencies(E ∈ {1,4,10})andtwodifferent
batchsizes(β ∈ {32,512}). Table4summarizestheparametersusedforthis
experiment.
   Figure4illustratestheaccuracyoftheglobalmodelovertimeforeachseed.
Thisfigurebringstwokeyinsights.First,thedifferentrunsexhibitconsequent
variability,especiallyintheearlystagesoftraining. Thisistruefortheruns
themselves,butalsoforbetweenrunsonthesamedatasets. Usingthesame
parameters,theaccuracyoftheglobalmodelvariesfrom0.2to0.8after100
epochson cicids(with β = 32)andfrom0.05to0.95on nb15. Someruns
presentsurprisinglyvolatileresults,suchastheseed6567on nb15(β = 512),
depictedinredinFigure4,whichstartsbelow0.4,thenincreasestocloseto
1.0,beforedroppingbelow0.2andstabilizing. Overall, nb15presentsahigher
variabilitythan cicids,butwithrunsthataremorestable.
   The dispersion decreaseswith time, givena largeenough batchsize, as
showninFigure5. Moreimportantly,eachrunprogressivelyconvergestoa
steadierstate.TheabsoluteaccuracydifferencesinthebottomrowsofFigure5
indeeddecreaseoverthefirstepochs,beforeplateauing. Itcanbeinterpreted
asaconsequenceofthecomplexityofthelearningtasks,whichbecomesharder
asclientspossessdifferentlabelsforsimilarsamples. Therefore,theproblem
probablyadmitsahighnumberoflocalminima,whicharereacheddepending
ontheseed.Incontrast,thedifferencebetweenroundsusingE = 32on cicids
(seeFigure5a)tendstoincreaseovertime,illustratingthedifficultyforeach
runtoconvergetoastablestate.


                                         14
```


### PDF page 16

[View original page, figures and tables](assets/page-016.png)

```text
(a) CIC-CSE-IDS2018.




























                                        (b) UNSW-NB15.

Figure5: Studyingattackimpactpredictabilityovertime,with50%attackers. The x-axis
representsthenumberoflocalepochs. Foreachsubfigure(Figures5aand5b),thetoprow
illustrateseachseed’saccuracyovertimewithitsstandarddeviation.Thebottomrowdisplays
themeanabsolutedifference(|accr−accr−1|)overtime.






                                                15
```


### PDF page 17

[View original page, figures and tables](assets/page-017.png)

```text
Table5:ExperimentparametersforRQ2

                               Dohyperparametersinfluencetheimpactofpoisoningattacks?

                               batch_size                 32,  128,  512
                               epochs                         100_10x10,  100_4x25,  100_1x100
                               distribution             10-0,  5-5
                               scenario                     continuous-100,  late-3,  redemption-3














                              5.2. HyperparametersImpact
                                  Tounderstandtheimpactofhyperparametersonthebehaviorofpoisoning
                              attacks,westudytheimpactofdifferentbatchsizes(β)andaggregationfre-
                              quencies(E).WesetagaintheconditionsfromSection5.1butlimitthenumber
                              ofepochsto100,asmostscenariosdonotshowsignificantchangesafterthis
                              point(seeSection5.1). Additionally,weevaluatethehyperparametersinthe
                              latepoisoningscenario,wheretheattackersonlystartaftera3-roundbootstrap
                              period,andintheredemptionscenario,wheretheattackersstopafter3rounds.
                              TheexperimentparametersaresummarizedinTable5.
                                  Figure6illustratestheinfluenceofhyperparametersontheimpactofpoison-
                              ingattacks.Thedifferences(thetwobottomrows)areshownonabi-symmetric
                              logarithmicscale[46],definedas

                                                       x′7→sgn(x)·log10      1+|   x10−4|  ,                 (6)

                              tomakeupfortheconsequentdifferencesinscalebetweencombinations. In
                              additiontotheaccuracyofeachparametercombination,Figure6alsopresents
                              theaveragechangeinstandarddeviation,or
                                                                 1    RX
                                                              R−1        σr−σr−1,                      (7)
                                                                     r=2
                              where Risthenumberofroundsand σristhestandarddeviationoftheac-
                              curacyatround rbetweenthedifferentseeds.Theaveragechangeaccuracyis
                              alsodisplayed. Forthesemetrics,apositivevalueindicatesanincreaseinthe
                              observedmetricovertime.


Answering RQ1 /Isthebehaviorofpoisoningattackspredictable?16

Thebehaviorofpoisoningattacksisnotpredictable,asthedispersion
betweenresultsistooimportant,althoughonlytheseedvaries.However,
thedispersiondecreasesovertimeinsomeconditions,andeachruntends
toconvergetoastablestate.Inpractice,thismakestheimpactdifficult
topredictforaspecificattackinstance,eventhoughgeneraltendencies
canbeextrapolated.
```


### PDF page 18

[View original page, figures and tables](assets/page-018.png)

```text
Figure6:Comparingtheinfluenceofhyperparametersontheimpactoflabel-flippingattacks
(τ ∈ {0,0.5}and α = 1). The x-axisrepresentsthenumberoflocalepochs. Thetoprow
illustratesthemeanaccuracyforeachcombinationofhyperparameters(βandE).Themiddle
rowdisplaysthemeandifferenceinstandarddeviation(σ)betweenrounds.Thebottomrow
showsthemeandifferenceintermsofaccuracybetweenrounds.




                                               17
```


### PDF page 19

[View original page, figures and tables](assets/page-019.png)

```text
(a) CIC-CSE-IDS2018.                           (b) UNSW-NB15.

Figure7: Impactofhyperparametersontheaccuracyoftheglobalmodelunderthe late
scenario.Thedataisalignedtostartatthelastbenignroundbeforetheattack,andtheimpact
ismeasuredoverthenext60epochs(i.e.,6,24or60roundsdependingontheaggregation
frequency).


   InthecontinuousscenariostudiedinFigure6(with τ = 0.5and α = 1),the
hyperparametershavelittleimpactontheaccuracyoftheglobalmodel.How-
ever, β = 32presentsaslightincreaseinaccuracyovertime(Figure6b)anda
decreaseindispersion(Figure6c). Notethatthereisclosetonodispersionin
theaccuracyofthebenignscenario,asdepictedinFigure6c,confirmingthat
theattackisindeedresponsibleforthedispersionobservedinSection5.1.Inter-
estingly,thecorrelationsbetweenthetwotesteddatasetsaremorepronounced
withsmallerbatchsizes,asshowninFigures6band6cwheretheresultsbecome
lesscorrelatedwith β = 512.
   Theotherhyperparametersdonotshowanysignificantcorrelation. Inthe
end,alltestedparametersleadtoanaccuracybetween0.4and0.5underpoi-
soning,whiletheyallexceed0.95withoutpoisoning. Thisiscriticallylowfor
intrusiondetection, as0.5isthescoreofarandomclassifieronabalanced
binary-classificationtask.Tossingacoinwouldyieldbetterresults.


                                          18
```


### PDF page 20

[View original page, figures and tables](assets/page-020.png)

```text
(a) CIC-CSE-IDS2018.                         (b) UNSW-NB15.

                             Figure8: Accuracyoftheglobalmodelafteralabel-flippingattack. Thedataisalignedto
                             startatthelastepochsbeforetheattackends,andtheimpactismeasuredoverthenext40
                             epochs(i.e.,4or10roundsdependingonE).


                                 However,whenclientshavebeengiventhetimetoconvergebeforetheat-
                             tack,theimpactofhyperparametersbecomesmorevisible,particularlyforthe
                             batchsize,asdepictedinFigure7. Whiletheimpactisinstantaneouswhen
                             β = 32,ittakesaround20epochswith β = 512toreachthesameaccuracy.
                             Thedispersionoftheresultsissignificantlylowerinthelatter,asisthereached
                             accuracy,whichgoesdownto0.25after60epochs. Abiggerbatchsizethus
                             leadstoagreaterinertiaandalowerdispersionoftheresultswhentheattack
                             starts,butalsotoaloweraccuracyafterward.
                                 Similarresultscouldbeexpectedintheredemption scenario, wherethe
                             attackstopsafter3rounds. However,Figure8presentsaquasi-instantaneous
                             recoveryoftheglobalmodel’saccuracyaftertheattackends.Thisisexpected,
                             asFigure3indicatesthattheaccuracyoftheglobalmodelalreadyexceeds0.95
                             atthefirstround,despitetherandomlyinitializedmodelparametersprovided
                             bytheserverbeforethefirstround. Thisisalsoconsistentwiththeresultsof
                             Zhangetal.[23]onNSL-KDD[37]andUNSW-NB15[38].













Answering RQ2 /Dohyperparametersinfluencetheimpactofpoisoning
attacks?
Althoughhyperparametershaveanimpactonthepoisoningeffect,no
combinationpreventsit:onaverage,theperformanceremainsthesame.
Thedispersionoftheresultscanvarysignificantlydependingonthecom-
binationofparameters,especiallywhentheattackoccursaftertheclients
haveconverged.Then,asmallerbatchsizeleadstoaswiftereffect,while19
alargerbatchsizeleadstoagreaterASR.Inperformance-constraineduse
cases(suchastheIoT)inparticular,history-baseddefensemechanisms
mightneedtoreactfastertomitigatetheattack’simpact.However,at-
tackshavelimitedpersistence,astheglobalmodel’saccuracyrecovers
almostinstantaneously. Consequently,strategiesshouldaccountforthe
dynamicbehaviorofattacks: swiftreactionisneededtodealwiththeir
almostimmediateimpact,whileofferingredemptionopportunities.
```


### PDF page 21

[View original page, figures and tables](assets/page-021.png)

```text
Table6:ExperimentparametersforRQ3

 AreIDSbackdoorsrealisticusinglabel-flippingattacks?

 distribution             10-0,  7-3,  5-5,  3-7
 target                         dos,  ddos,  bot,  infiltration,  injection
 scenario                     continuous-100
 dataset                       cicids,  nb15


5.3. IDSBackdoorsusingLabel-flipping
   Oneofthemainconcernswithpoisoningattacksistheperspectiveofback-
doorsintheIDS,allowingattackerstobypassthesystem’sdetectioncapabili-
tiesafterward.Toassessthisrisk,westudytheimpactoflabel-flippingattacks
withdifferenttargets.Weconsider α = 100%andvariousvaluesof τtoassess
whetheraASRof1.0canbeachieved.Table6summarizestheparametersused
forthisexperiment.
   Figure9presentstheimpactoflabel-flippingattacksontheaccuracyofthe
globalmodelfordifferentattacktargets.ThefiguresshowtheRASRoftargeted
attackstowardsthedifferentclassesavailableineachdataset. Tomeasurethe
impactoftheattackontheoverallperformanceofthemodel,wealsomeasure
theMTAunderthedifferentattacks. TheAASRofthebenignscenariois
providedasareference(cf.Figure3).
   Thefirststrikingobservationisthattheresultsdiffergreatlybetweenthe
twodatasets.Whileon cicids,someattackscanreachanASRcloseto1.0given
enoughattackers,mostresultson nb15remainbelow0.25. Someclassesseem
completelyimmunetotheattack,suchas“Backdoor”,“Shellcode”,and“Worms”.
Eventhemostsuccessfulattackson nb15barelyexceed0.5.On cicids,onthe
otherhand,theresultsaremoreconvincing.Although30%oftheattackersare
notenoughtopermanentlyimpacttheglobalmodel’saccuracy,multipleclasses
canreachaRASRcloseto1.0atleastmomentarily.With τ = 0.5,theRASR
of“Bot”,“DDoS”,and“Infiltration” classespermanentlyreach1.0afterafew
rounds. Mostimportantly,theMTAoftheglobalmodelremainsclosetoits
nominalperformance,evenwhentheRASRofthetargetedclassesreaches1.0,
exceptforthe“DDoS”class. Indeed,the“DDoS”classisthemostrepresented
inthedataset,with5.29%ofthesamples. Therefore,themisclassificationof
roughly70%ofthesamplesofthisclassleadstoamoresignificantimpacton
theaccuracyoftheglobalmodel.
   Theresultdisparitybetweenclasses,andmoreimportantlybetweendatasets,
isdifficulttointerpret,althoughmultiplehypothesescanbeformulated.First,
someclassesaresignificantlylessrepresentedinthedatasetssuchas“Injection”
in cicidsor“Analysis”,“Backdoor”,“Shellcode”,and“Worms”innb15(seeTa-
ble1). AllthesetargetsyieldedaRASRcloseto0.0. Second,asweconsider
binaryclassificationtasks,anyoverlapbetweentheclasses’characteristicscan
beusedbythemodeltoinferthecorrectassociationsusingsamplesfromunaf-
fectedclasses.Forinstance,the“BruteForce”and“DoS”classesincicidsboth



                                         20
```


### PDF page 22

[View original page, figures and tables](assets/page-022.png)

```text
(a) CIC-CSE-IDS2018.






































                                        (b) UNSW-NB15.

Figure9: RASRoftargetedlabel-flippingattacksovertime,with β  = 512, E  = 10,and
α = 1.0.The x-axisrepresentsthenumberoflocalepochs.TheAASRofthebenignscenario
isprovidedasareferenceforeachtargetedclass.




                                                21
```


### PDF page 23

[View original page, figures and tables](assets/page-023.png)

```text
Table7:ExperimentparametersforRQ4

                               Isthereacriticalthresholdwherelabel-flippingattacksbeginto
                               impactperformance?

                               distribution             10-0,  9-1,  7-3,  5-5,  3-7
                               scenario                     continuous-{10,30,60,70,80,90,95,99,100}
                               target                         untargeted,  dos,  ddos,  bot,  infiltration
                               dataset                       cicids,  nb15


                             implyahighnumberofconnectionsfromasinglehost,andbothobtainsubpar
                             resultswhencomparedtothemostefficientattacks.
















                             5.4. ThresholdforEffectiveAttacks
                                 Section5.3suggeststhatthenumberofattackersisacriticalfactorinthe
                             effectivenessoftargetedattacks.Thisexperimentaimstounderstandthecrit-
                             icalthresholdwherelabel-flippingattacksbegintoimpacttheglobalmodel’s
                             accuracybystudyingbothDPR(α)andMPR(τ). Table7summarizesthe
                             parametersusedforthisexperiment.Ourpreviousexperimentshighlightedthe
                             impactofthenumberofattackersontheaccuracyoftheglobalmodel.
                                 Figure10presentstheRASRofconsideredlabel-flippingattacksovertime,
                             bothforuntargetedandtargetedattacks. Theentirefigureemphasizesthe
                             importanceofthenumberofattackersintheeffectivenessoftheattack,asmost
                             attacksarenotimpactfulwhile τ ≤ 0.3.Inparticular,withonesingleattacker
                             (τ = 0.1),theRASRremainswellbelow0.1,evenwithahighpoisoningrate
                             (α = 1.0).  τ = 0.5representsatippingpointinourtests,withRASRvalues
                             ordersofmagnitudehigherthanwith τ = 0.3.
                                 Moreimportantly,wecaninferfromΓ =τ×αthetotalquantityofpoisoned
                             dataduetoourIIDpartitioning.Foruntargetedattacksin cicids,theRASR
                             exceeds0.5for Γ > 0.5andapproaches1.0for Γ > 0.67. Fortargetedattacks,
                             theRASRexceeds0.5forΓ> 0.49andapproaches1.0forΓ> 0.56.Untargeted
                             attackson nb15areslightlymoreeffective,withtheRASRexceeding0.5forΓ>
AnsweringRQ3/AreIDSbackdoorsrealisticusinglabel-flippingattacks?0.49andapproaching1.0for Γ > 0.63.However,ashighlightedinSection5.3,
                             targetedattackson nb15areclosetoineffective,withtheRASRneverexceeding
Thistypeofattackhaslessimpactontheglobalmodel’sMTA,meaning
thattheyaremorelikelytoremainundetected.Althoughnotallclasses22
areequallyaffected,IDSbackdoorsarepossibleusinglabel-flippingat-
tacks,givenasufficientnumberofattackersandawell-representedtarget.
Colludingattackerscanrealisticallycreateabackdoorthatmaylaterbe
leveragedtoevadedetection,raisingthequestionoftheminimumDPR
andMPRnecessaryforsuchattackstobeeffective.However,theresults
aredataset-dependent,andsomeclassesremaincompletelyimmuneto
theattackinourexperiments,especiallyin nb15.
```


### PDF page 24

[View original page, figures and tables](assets/page-024.png)

```text
(a) CIC-CSE-IDS2018





























                                       (b) UNSW-NB15

Figure10: EvolutionoftheRASRofpoisoningattacksovertime,dependingonthelocal
poisoningrate(α),theproportionofattackers(τ),andthetypeofattack.The x-axisrepre-
sentsthenumberofrounds. Thevaluefortargetedattacksisthemeanofthetargets,from
whichweexcludetheunder-representedandineffectiveones(seeFigure9):“Infiltration”and
“Injection”incicids,and“Analysis”,“Backdoor”,“Shellcode”,and“Worms”innb15. TheFL
roundisusedasthetimeunit.





                                              23
```


### PDF page 25

[View original page, figures and tables](assets/page-025.png)

```text
Table8:ExperimentparametersforRQ5

                               Areexistingtechniqueswell-suitedtodetectlabel-flippingattacks?

                               distribution             10-0,  9-1,  5-5
                               scenario                     continuous-100
                               target                         untargeted
                               partitioner               iid_drop_1,  kmeans_drop_1,  iid_drop_2,  kmeans_drop_2,
                                                    iid_keep_1,  iid_full,  kmeans_full,  kmeans_keep_1
                               dataset                       cicids,  nb15


                              0.25,evenwith Γ = 0.7,ourhighestoverallpoisoningrate. Thus,RASRand
                              thetuple (α,τ)exhibitfairlysimilarvariations,albeitnotlinear: thehigher
                              theDPRandMPR,thehighertheRASR.However,poisoningtheentirelocal
                              datasetseemsmorepowerfulthaninstantiatingmoreattackers: α = 100and
                              τ  = 50yieldhigherRASRthan α  = 80and τ  = 70, althoughthelatter
                              representsmoreaffecteddataoverall.














                              5.5. SimilarityasaDefenseMechanism
                                  Asignificantamountofliteraturehasbeendedicatedtothedevelopment
                              ofdefensemechanismsagainstpoisoningattacks.Oneofthemostrepresented
                              strategiesistheuseofsimilaritymetricstodetectpoisonedcontributions[21,
                              28,29,47]. Thisreliesontheassumptionthattheattackers’modelupdates
                              arestatisticallydifferentfromthoseofbenignparticipants,andthataprofileof
                              eitherofthosecanbeestablished.Forinstance,Tolpeginetal.[11]proposeusing
                              PCAtomeasurethedistancebetweenmodelupdatesintheprojectedspace.
                              ToassesstheeffectivenessofthisstrategyforCIDSs,weexploretheimpactof
                              differentpartitioningschemes(cf.Section4.4.1)onthePCAanalysis.Table8
                              summarizestheparametersusedforthisexperiment.
                                  Figure11presents2Dprojectionsoftheparticipants’gradientsusingPCA
                              fordifferentpartitioningschemes. Eachpointrepresentsaclient’scontribu-
                              tiontotheglobalmodel’supdateinthe10thround. Since FedAvgaggregates
                              modelsbydefault,wecomputethegradients gri asthedifferencebetweenthe
                              participant’smodelatroundrandthelastglobalmodel,i.e.,
Answering RQ4 /Isthereacriticalthresholdwherelabel-flippingattacksgri = ¯wr−1−wri.                        (8)
begintoimpactperformance?
Theeffectivenessoflabel-flippingattacksisdirectlyrelatedtotheoverall24
quantityofpoisoneddata. However,thisrelationshipisnotlinearand
thereisacriticalthresholdwhen αisbelow1.0. FLsuffersfromthe
samecaveatasnumerousotherdistributedsystems,wherethemajority
ofparticipantsmustbehonesttoensurethesystem’ssecurity.However,
eveninitsdefaultconfigurationandwithoutanydefensemechanisms,
multipleattackersarenecessarytoimpacttheglobalmodel’saccuracy.
```


### PDF page 26

[View original page, figures and tables](assets/page-026.png)

```text
(a) Single attacker on CIC-CSE-IDS2018                    (b) Single attacker on UNSW-NB15
















(c) Colluding attackers on CIC-CSE-IDS2018                (d) Colluding attackers on UNSW-NB15

Figure11:2DprojectionofgradientsusingPCAfordifferentpartitioningschemes.Thetop
rowrepresentstheresultsforasingleattacker(i.e., τ = 0.1),whilethebottomrowillustrates
theresultsforcolludingattackers(i.e., τ = 0.5). Resultsforthe10throundwith seed=1128
and α = 1.0.















                                                   25
```


### PDF page 27

[View original page, figures and tables](assets/page-027.png)

```text
Thisallowsustocomparetheparticipants’directionratherthantheirposition
                             inthemodelparameterspace.
                                 Theresultsinthe iid_fullsettingareconsistentwiththeliterature: be-
                             nignparticipants’contributionsaretightlyclustered,andtheattacker’scontri-
                             butionsareeasilyidentifiableasoutliers[11].However,themoreheterogeneous
                             partitioningschemesmakeitlessclear,especiallywithasingleattacker. For
                             instance,the kmeans_keep_1partitioningschemeon cicids(Figure11a)dis-
                             playstwooutliersthatareroughlyequalyfarfromthebenignparticipants,one
                             ofwhichistheattacker. Inthe kmeans_*schemes,theattackerissometimes
                             indistinguishablefromthebenignparticipants. Colludingattackersaremore
                             easilyidentifiable,astheyareusuallygroupedtogetherinthelessheteroge-
                             neoussettings. Thisqualitydisappearswiththe kmeans_*schemes,especially
                             with cicids(Figure11c).Thetwodatasetsexhibitslightlydifferentbehaviors,
                             withattackersbeingmoreeasilyidentifiableon nb15thanon cicids,depending
                             onthepartitioningscheme.


















                             6. Discussion

                             6.1. Maintakeaways
                             AttackEffectiveness. Label-flippingattackscansignificantlydegradetheper-
                             formanceofFLmodelsforIDSs,theireffectivenessbeingdirectlyrelatedto
                             thetotalquantityofpoisoneddata.InIIDsettings,thiscanbeapproximated
                             bytheproductofDPR(α)andMPR(τ),butthisrelationshipisdistribution-
                             dependent. However,theseattacksarenotverypracticalbecauseofthehigh
                             numberofmaliciousparticipantsrequiredforsignificantimpact. Theycan,
                             nonetheless,effectivelymodelvariousdataqualityissuesintraining,suchas
                             mislabeledevents(e.g.,anentireeventmissedbytheoperator)ornoisydata
Answering RQ5 / Are existing techniques well-suited to detect label-(e.g.,multiplelabelsforsimilarsamples).

flippingattacks?             IDSEvasionwithTargetedAttacks. Targetedattacksareparticularlyeffective
ThePCAanalysisprovidesaneasyandvisualwaytodetectattackers,againstwell-detectedtargets,althoughtheirsuccesscanbemitigatedbythe
aslongasthedatadistributionissufficientlyhomogeneous. However,
thisdefensemechanismisparticularlychallengedinmoreheterogeneous26
settings.Colludingattackersaremoreeasilyidentifiableastheywillusu-
allyformaclusteroftheirown,highlightingtherelevanceofmitigation
strategiessuchas FoolsGold[21]and CONTRA[29]whichdetectcolluding
attackersinheterogeneousenvironmentsusingtheirsimilarity. Overall,
similarity-baseddefensemechanismsareeffectiveindetectingattackers
inhomogeneousenvironments,buttheireffectivenessdecreaseswiththe
heterogeneityofthedatadistribution.
```


### PDF page 28

[View original page, figures and tables](assets/page-028.png)

```text
model’sgeneralizationcapabilities(Section5.3). Thisslightlycontradictsthe
observationsmadebyTolpeginetal.[11],whichcanbeexplainedbytheclass
overlapinherenttoIDSusecases. Formoreeffectiveevasiontechniques,ML
backdoors,asreviewedbyMerzouketal.[24],maybemoresuitable.

ImplicationsforDefenseandOperation. Whilelabel-flippingattackscanpose
athreattoFL-basedIDSs,theyrequiresignificantresourcestobeeffective,
suggestingsomeinherentresilience. However,propermonitoringanddefense
mechanismsremainessential,especiallyinscenarioswheredataqualitycannot
beguaranteed. Gradientsimilarityanalysiscanbeeffectivefordetection(see
Section2.3),althoughitsreliabilitydecreasesinheterogeneoussettings(Sec-
tion5.5). Mitigationstrategiesmustalsobecarefullytailoredtoaccountfor
thedynamicbehaviorofattacks,particularlyinconstrainedenvironmentssuch
asIoT(Section5.2).

6.2. Limitationsofthisstudy
   Systematicallyreviewingthebehaviorofsuchcomplexsystemsinvolvesa
significantnumberofvariables.Asaresult,thenumberofexperimentsrequired
tocoverallpossiblescenariosisimpractical. Wemadecriticalchoicesinthe
evaluation,anddiscussbellowthecaveatsassociatedwiththem.

Scalability. Theexperimentscarriedoutinthisstudyarelimitedtoasmall
numberofparticipants(i.e.,10)anddonotaccountforvariationsinthisnum-
ber.Whilethissettingisrepresentativeofreal-worldcollaborativeusecases,a
typicalcross-silofederationbetweenorganizations,itsscalabilitycanbeques-
tioned. However,somerelatedstudies[24,35]haveshownthattheimpactof
poisoningattacksisnotsignificantlyinfluencedbythenumberofparticipants,
aslongastheproportionsofmaliciousparticipantsarepreserved. Wethus
expecttheseexperimentstoactsimilarlywithalargernumberofparticipants.

HeterogeneitySimulation. WhileRQ5touchesonthetopicofdatadistribution,
itfocusesonacaricaturaldepictionthatisnotfullyrepresentativeofareal-
worldsetting.Infact,allevaluationsthatrelyonpartitioningdatasetsamong
participantsarelimitedbydesignintheirrepresentativeness,notablydueto
thedependenciesbetweentrainingsamples.Althoughwecanexpecttheresults
ofSection5.5tobeapplicabletootherdatadistributions,thisalsoemphasizes
theneedforindependentdatasetstailoredfordistributedintrusiondetection.

Generalizabilityoftheresults. Moregenerally,thedifferencesobservedbetween
theresultsonthetwoconsidereddatasets(i.e.,UNSW-NB15andCSE-CIC-
IDS2018)raisethequestionofwhethertheresultsobservedherecanbegen-
eralizedtootherdatasetsandreal-worlddeployments. Whilecorrelationscan
beobservedwithexistingwork[23,36],includingonotherdatasetswithNSL-
KDD[23],thelackofacommonbenchmarkforfederatedintrusiondetection
systemsmakesitdifficulttocomparetheresultsofdifferentstudies.Thiscalls
forextendedevaluationsofotherdatasetsandmodels,aswellasthedevelop-
mentofacommonbenchmarkfordistributedIDSs.


                                         27
```


### PDF page 29

[View original page, figures and tables](assets/page-029.png)

```text
7. ConclusionandTakeaways

   TheliteratureontheimpactofpoisoningattacksonFLthatspecifically
coverintrusiondetectionusecasesisscarce,andinit,label-flippingattacks
havebeenoverlooked. Thispaperfillsthisgapbyprovidingacomprehensive
analysisoftheimpactoflabel-flippingattacksonFLforIDSs.Weevaluatedthe
impactofuntargetedandtargetedlabel-flippingattacksontheperformanceof
FLmodelstrainedonCSE-CIC-IDS2018andUNSW-NB15usingastandardized
featuresettoallowextensionofthiswork.
   Ourresultshighlightthat(i)label-flippingattackscanhaveasignificant
impactontheperformanceofFLmodels,buttheirsuccessrateistiedtothe
numberofflippedsamplesoverall;(ii)IDSbackdoorsusinglabel-flippingat-
tackscanbesignificantlymitigatedbythemodel’sgeneralizationcapabilities;
(iii)mitigationstrategiesmustbeadaptedtotheusecasespecificities(   e.g.,
constrainedenvironments);(iv)gradientsimilarity      can beusedtodetectla-
bel-flippingattacks,butitseffectivenessischallengedinheterogeneoussettings.
   However,manyopenquestionsremaintobeaddressed. First,whilethe
comparisonwithexistingworksseemstocorroborateourresults,thisstudy
callstobeextendedtootherdatasets,featuresets,modelarchitectures,andFL
aggregationstrategies,butalsotolarger-scaleusecases. Second,theprovided
evaluationframeworkcanbeusedtoevaluatetheefficiencyofexistingcounter-
measuresortodevelopnewones.Consequently,evaluatingexistingdefensesin
thesesettingsisacriticalnextstepofthiswork.Finally,thisstudyalsohigh-
lightscommunity-widelimitationsinevaluatingFLmodelsforIDSs,notably
thelackofappropriatedatasetsandacommonbenchmark.Westronglybelieve
thatthisworkisafirststepinthisdirectionandadvocateforbetterevalua-
tionandcomparisonofFLmodelsandaggregationstrategiesinthecontextof
intrusiondetection.


References

 [1]B. McMahan, E. Moore, D. Ramage, S. Hampson, B. A. y Arcas,
     Communication-efficientlearningofdeepnetworksfromdecentralizeddata,
     in: A.Singh,J.Zhu(Eds.),Proceedingsofthe20thInternationalCon-
     ferenceonArtificialIntelligenceandStatistics,volume54ofProceedings
     ofMachineLearningResearch,PMLR,2017-04-20/2017-04-22,pp.1273–
     1282.

 [2]T.D.Nguyen,S.Marchal,M.Miettinen,H.Fereidooni,N.Asokan,A.-
     R.Sadeghi, DÏoT:AFederatedSelf-learningAnomalyDetectionSystem
     for IoT, in: 2019 IEEE 39th International Conference on Distributed
     ComputingSystems(ICDCS),volume2019-July,IEEE,2019,pp.756–767.
     doi:10.1109/ICDCS.2019.00080.

 [3]H.Liu,S.Zhang,P.Zhang,X.Zhou,X.Shao,G.Pu,Y.Zhang,Blockchain
     andFederatedLearningforCollaborativeIntrusionDetectioninVehicular


                                         28
```


### PDF page 30

[View original page, figures and tables](assets/page-030.png)

```text
EdgeComputing,IEEETrans.Veh.Technol.70(2021)6073–6084.doi:10.
    1109/TVT.2021.3076780.

 [4]S.Agrawal,S.Sarkar,O.Aouedi,G.Yenduri,K.Piamrat,M.Alazab,
    S.Bhattacharya,P.K.R.Maddikunta,T.R.Gadekallu,FederatedLearn-
    ingforintrusiondetectionsystem: Concepts, challengesandfuturedi-
    rections, ComputerCommunications195(2022)346–361.doi:10.1016/j.
    comcom.2022.09.012.

 [5]L.Lavaur,M.-O.Pahl,Y.Busnel,F.Autrel, TheEvolutionofFederated
    Learning-basedIntrusionDetectionandMitigation: ASurvey, TNSM
    (2022).

 [6]M.Alazab,S.P.RM,P.M,P.Reddy,T.R.Gadekallu,Q.-V.Pham,
    FederatedLearningforCybersecurity: Concepts,ChallengesandFuture
    Directions,IEEETrans.Ind.Inf.(2021)1–1.doi:10/gnm4dj.

 [7]E.Fedorchenko,E.Novikova,A.Shulepov, ComparativeReviewofthe
    IntrusionDetectionSystemsBasedonFederatedLearning: Advantages
    andOpenChallenges,Algorithms15(2022)247.doi:10.3390/a15070247.

 [8]B.Ghimire,D.B.Rawat, RecentAdvancesonFederatedLearningfor
    CybersecurityandCybersecurityforFederatedLearningforInternetof
    Things,IEEEInternetofThingsJournal9(2022)8229–8249.doi:10.1109/
    JIOT.2022.3150363.

 [9]E.M.Campos,P.F.Saura,A.González-Vidal,J.L.Hernández-Ramos,
    J.B.Bernabé,G.Baldini,A.Skarmeta,EvaluatingFederatedLearningfor
    intrusiondetectioninInternetofThings:Reviewandchallenges,Computer
    Networks203(2022)108661.doi:10.1016/j.comnet.2021.108661.

[10]A.N.Bhagoji,S.Chakraborty,P.Mittal,S.Calo, AnalyzingFederated
    LearningthroughanAdversarialLens, in: Proceedingsofthe36thInter-
    nationalConferenceonMachineLearning,PMLR,2019,pp.634–643.

[11]V.Tolpegin, S.Truex, M.E.Gursoy, L.Liu, DataPoisoningAttacks
    Against Federated Learning Systems,  in: L. Chen, N. Li, K. Liang,
    S.Schneider(Eds.),ComputerSecurity–ESORICS2020,LectureNotes
    inComputerScience,SpringerInternationalPublishing,Cham,2020,pp.
    480–501.doi:10.1007/978-3-030-58951-6_24.

[12]D.J.Beutel, T.Topal, A.Mathur, X.Qiu, T.Parcollet, N.D.Lane,
    Flower: Afriendlyfederatedlearningresearchframework, arXivpreprint
    arXiv:2007.14390(2020). arXiv:2007.14390.

[13]O.Yadan,Hydra-Aframeworkforelegantlyconfiguringcomplexapplica-
    tions,Github,2019.




                                        29
```


### PDF page 31

[View original page, figures and tables](assets/page-031.png)

```text
[14]L.Lavaur,Y.Busnel,F.Autrel, Systematicanalysisoflabel-flippingat-
    tacksagainstfederatedlearningincollaborativeintrusiondetectionsys-
    tems,in:Proceedingsofthe19thInternationalConferenceonAvailability,
    ReliabilityandSecurity(ARES),Vienna,Austria,2024.

[15]P.Kairouz,H.B.McMahan,B.Avent,A.Bellet,M.Bennis,A.N.Bhagoji,
    K.Bonawitz,Z.Charles,G.Cormode,R.Cummings,R.G.L.D’Oliveira,
    H.Eichner,S.E.Rouayheb,D.Evans,J.Gardner,Z.Garrett,A.Gascón,
    B. Ghazi, P. B. Gibbons, M. Gruteser, Z. Harchaoui, C. He, L. He,
    Z.Huo,B.Hutchinson,J.Hsu,M.Jaggi,T.Javidi,G.Joshi,M.Khodak,
    J.Konečný,A.Korolova,F.Koushanfar,S.Koyejo,T.Lepoint,Y.Liu,
    P.Mittal,M.Mohri,R.Nock,A.Özgür,R.Pagh,M.Raykova,H.Qi,
    D.Ramage, R.Raskar, D.Song, W.Song, S.U.Stich, Z.Sun, A.T.
    Suresh,F.Tramèr,P.Vepakomma,J.Wang,L.Xiong,Z.Xu,Q.Yang,
    F.X.Yu,H.Yu,S.Zhao, AdvancesandOpenProblemsinFederated
    Learning,arXiv:1912.04977[cs,stat](2021). arXiv:1912.04977.

[16]Y.Huang,L.Chu,Z.Zhou,L.Wang,J.Liu,J.Pei,Y.Zhang,Personalized
    Cross-SiloFederatedLearningonNon-IIDData, AAAI35(2021)7865–
    7873.doi:10.1609/aaai.v35i9.16960.

[17]L.Lavaur,Y.Busnel,F.Autrel,Demo:Highlightingthelimitsoffederated
    learninginintrusiondetection, in: Proceedingsofthe44thInternational
    ConferenceonDistributedComputingSystems(ICDCS),JerseyCity,NJ,
    USA,2024.

[18]N. Rodríguez-Barroso, D. Jiménez-López, M. V. Luzón, F. Herrera,
    E.Martínez-Cámara,Surveyonfederatedlearningthreats:Concepts,tax-
    onomyonattacksanddefences,experimentalstudyandchallenges,Infor-
    mationFusion90(2023)148–173.doi:10.1016/j.inffus.2022.09.011.

[19]L.Lamport,R.Shostak,M.Pease, TheByzantinegeneralsproblem, in:
    Concurrency: TheWorksofLeslieLamport,AssociationforComputing
    Machinery,NewYork,NY,USA,1982,pp.203–226.

[20]J. R. Douceur,  The Sybil Attack,  in:  P. Druschel, F. Kaashoek,
    A.Rowstron(Eds.), Peer-to-PeerSystems, LectureNotesinComputer
    Science, Springer, Berlin, Heidelberg, 2002, pp. 251–260. doi:10.1007/
    3-540-45748-8_24.

[21]C.Fung,C.J.M.Yoon,I.Beschastnikh, TheLimitationsofFederated
    LearninginSybilSettings,in:23rdInternationalSymposiumonResearch
    inAttacks,IntrusionsandDefenses({RAID}2020),{USENIX}Associa-
    tion,SanSebastian,2020,pp.301–316.

[22]M.Fang, X.Cao, J.Jia, N.Gong, LocalModelPoisoningAttacksto
    Byzantine-RobustFederatedLearning,in:29thUSENIXSecuritySympo-
    sium(USENIXSecurity20),2020,pp.1605–1622.


                                        30
```


### PDF page 32

[View original page, figures and tables](assets/page-032.png)

```text
[23]Y.Zhang,Y.Zhang,Z.Zhang,H.Bai,T.Zhong,M.Song,Evaluationof
    datapoisoningattacksonfederatedlearning-basednetworkintrusiondetec-
    tionsystem,in:2022IEEE24thIntConfonHighPerformanceComputing
    &Communications;8thIntConfonDataScience&Systems;20thIntConf
    onSmartCity;8thIntConfonDependabilityinSensor,Cloud&BigData
    Systems & Application (HPCC/DSS/SmartCity/DependSys), 2022, pp.
    2235–2242.doi:10.1109/HPCC-DSS-SmartCity-DependSys57074.2022.00330.
[24]M.A.Merzouk,F.Cuppens,N.Boulahia-Cuppens,R.Yaich,Parameter-
    izingpoisoningattacksinfederatedlearning-basedintrusiondetection,in:
    Proceedingsofthe18thInternationalConferenceonAvailability,Reliabil-
    ityandSecurity,ARES’23,AssociationforComputingMachinery,New
    York,NY,USA,2023,pp.1–8.doi:10.1145/3600160.3605090.

[25]P.Blanchard,E.M.ElMhamdi,R.Guerraoui,J.Stainer,Machinelearning
    withadversaries:Byzantinetolerantgradientdescent,AdvancesinNeural
    InformationProcessingSystems30(2017).
[26]D.Yin,Y.Chen,R.Kannan,P.Bartlett, Byzantine-RobustDistributed
    Learning:TowardsOptimalStatisticalRates,in:Proceedingsofthe35th
    InternationalConferenceonMachineLearning,PMLR,2018,pp.5650–
    5659.
[27]S.Shen,S.Tople,P.Saxena, Auror:Defendingagainstpoisoningattacks
    incollaborativedeeplearningsystems, in: Proceedingsofthe32ndAn-
    nualConferenceonComputerSecurityApplications,ACM,NewYork,NY,
    USA,2016,pp.508–519.doi:10.1145/2991079.2991125.

[28]T.D.Nguyen,P.Rieger,H.Chen,H.Yalame,H.Möllering,H.Fereidooni,
    S.Marchal,M.Miettinen,A.Mirhoseini,S.Zeitouni,F.Koushanfar,A.-R.
    Sadeghi,T.Schneider,FLAME:TamingBackdoorsinFederatedLearning,
    in: 31stUSENIXSecuritySymposium(USENIXSecurity22),2022,pp.
    1415–1432.

[29]S.Awan,B.Luo,F.Li, CONTRA:DefendingAgainstPoisoningAttacks
    inFederatedLearning, in: E.Bertino,H.Shulman,M.Waidner(Eds.),
    ComputerSecurity–ESORICS2021,LectureNotesinComputerScience,
    SpringerInternationalPublishing,Cham,2021,pp.455–475.doi:10.1007/
    978-3-030-88418-5_22.
[30]L.Zhao,S.Hu,Q.Wang,J.Jiang,C.Shen,X.Luo,P.Hu,Shielding
    CollaborativeLearning:MitigatingPoisoningAttacksthroughClient-Side
    Detection,2020. arXiv:1910.13111.
[31]L.Lavaur,P.-M.Lechevalier,Y.Busnel,R.Ludinard,G.Texier,M.-O.
    Pahl, RADAR:Modelqualityassessmentforreputation-awarecollabora-
    tivefederatedlearning, in: Proceedingsofthe43rdInternationalSym-
    posiumonReliableDistributedSystems(SRDS),Charlotte, NC,USA,
    2024-09,2024.


                                        31
```


### PDF page 33

[View original page, figures and tables](assets/page-033.png)

```text
[32]F.Nuding,R.Mayer,DataPoisoninginSequentialandParallelFederated
    Learning, in: Proceedingsofthe2022ACMonInternationalWorkshop
    onSecurityandPrivacyAnalytics,ACM,BaltimoreMDUSA,2022,pp.
    24–34.doi:10.1145/3510548.3519372.

[33]G.Sun,Y.Cong,J.Dong,Q.Wang,L.Lyu,J.Liu,DataPoisoningAttacks
    onFederatedMachineLearning,IEEEInternetofThingsJournal9(2022)
    11365–11375.doi:10.1109/JIOT.2021.3128646.
[34]T.D.Nguyen,P.Rieger,M.Miettinen,A.-R.Sadeghi,PoisoningAttacks
    onFederatedLearning-basedIoTIntrusionDetectionSystem,in:Proceed-
    ings2020WorkshoponDecentralizedIoTSystemsandSecurity,Internet
    Society,SanDiego,CA,2020.doi:10.14722/diss.2020.23003.

[35]N.C.Vy,N.H.Quyen,P.T.Duy,V.-H.Pham,FederatedLearning-Based
    IntrusionDetectionintheContextofIIoTNetworks: PoisoningAttack
    andDefense, in: M.Yang,C.Chen,Y.Liu(Eds.),NetworkandSystem
    Security,volume13041,SpringerInternationalPublishing,Cham,2021,
    pp.131–147.doi:10.1007/978-3-030-92708-0_8.

[36]R.Yang,H.He,Y.Wang,Y.Qu,W.Zhang,Dependablefederatedlearn-
    ingforIoTintrusiondetectionagainstpoisoningattacks, Computers&
    Security132(2023)103381.doi:10.1016/j.cose.2023.103381.
[37]M.Tavallaee,E.Bagheri,W.Lu,A.A.Ghorbani, Adetailedanalysisof
    theKDDCUP99dataset,in:2009IEEESymposiumonComputational
    IntelligenceforSecurityandDefenseApplications,Cisda,IEEE,2009,pp.
    1–6.doi:10.1109/CISDA.2009.5356528.

[38]N.Moustafa,J.Slay,UNSW-NB15:Acomprehensivedatasetfornetwork
    intrusiondetectionsystems(UNSW-NB15networkdataset), in: 2015
    MilitaryCommunicationsandInformationSystemsConference(MilCIS),
    2015,pp.1–6.doi:10.1109/MilCIS.2015.7348942.
[39]ACM,      Artifact      Review      and      Badging      v1.1,
    https://www.acm.org/publications/policies/artifact-review-and-badging-
    current,2020.

[40]M.Sarhan,S.Layeghy,M.Portmann, TowardsaStandardFeatureSet
    forNetworkIntrusionDetectionSystemDatasets, MobileNetwAppl27
    (2022)357–370.doi:10.1007/s11036-021-01843-0.
[41]S.Layeghy,M.Portmann,OnGeneralisabilityofMachineLearning-based
    NetworkIntrusionDetectionSystems,2022. arXiv:2205.04112.

[42]M.Sarhan,S.Layeghy,M.Portmann,TowardsaStandardFeatureSetfor
    NetworkIntrusionDetectionSystemDatasets,2021. arXiv:2101.11315.
[43]ntop,nprobe-anextensiblenetflowv5/v9/ipfixprobeforipv4/v6,????
    URL: https://www.ntop.org/products/netflow/nprobe/.


                                        32
```


### PDF page 34

[View original page, figures and tables](assets/page-034.png)

```text
[44]I. Sharafaldin, A. Habibi Lashkari, A. A. Ghorbani,  Toward Gener-
     atingaNewIntrusionDetectionDatasetandIntrusionTrafficCharac-
     terization, in: Proceedings ofthe 4th InternationalConferenceon In-
     formation Systems Security and Privacy, SCITEPRESS - Science and
     TechnologyPublications,Funchal,Madeira,Portugal,2018,pp.108–116.
     doi:10.5220/0006639801080116.

[45]S.I.Popoola,G.Gui,B.Adebisi,M.Hammoudeh,H.Gacanin,Federated
     DeepLearningforCollaborativeIntrusionDetectioninHeterogeneousNet-
     works, in: 2021IEEE94thVehicularTechnologyConference(VTC2021-
     Fall),2021,pp.1–6.doi:10.1109/VTC2021-Fall52928.2021.9625505.

[46]J.B.W.Webber,Abi-symmetriclogtransformationforwide-rangedata,
     Meas.Sci.Technol.24(2012)027001.doi:10.1088/0957-0233/24/2/027001.

[47]X.Cao,M.Fang,J.Liu,N.Z.Gong,FLTrust:Byzantine-robustFederated
     LearningviaTrustBootstrapping,2022.doi:10.48550/arXiv.2012.13995.
     arXiv:2012.13995.




































                                         33
```
