# Resilient Federated Ensemble Learning for IoT Intrusion Detection in Adversarial and Imbalanced Environments

**Authors:** Arvind Prasad; Ibrahim Aljubayri; Mohammad Zubair Khan; Abdulfattah Noorwali

**Publication:** Computer Modeling in Engineering & Sciences (2026).

**Publication DOI:** https://doi.org/10.32604/cmes.2026.082021

**Verified free PDF:** https://cdn.techscience.cn/files/CMES/2026/TSP_CMES-147-3/TSP_CMES_82021/TSP_CMES_82021.pdf

**Downloaded version:** Publisher version of record, open access, Creative Commons Attribution 4.0.

**Qualification:** Q2, ENGINEERING, MULTIDISCIPLINARY. Journal rankings use the 2024 JIF category quartile (June 2025 JCR), not an asserted 2026 ranking.

**Integrity:** 29 pages; 11,115,059 bytes; SHA-256 `7cbce88079958757be0ec2e477d6c5cacb6146baf7eb7704d30f41aa5b620014`. Verified 8 October 2026.

## Reading and extraction note

The PDF is the authoritative complete manuscript. Below is automatic page-level text extraction, not a newly authored summary or a verbatim-quality transcription. Two-column order, formulas, ligatures and table spacing can be imperfect. Every page has a rendered PNG in `assets/` for inspecting figures, equations and tables at their original locations. Publication metadata is saved alongside the images. The technical review is in [the selection audit](../phase2-selection-audit.md).

## Full manuscript text


### PDF page 1

[View original page, figures and tables](assets/page-001.png)

```text
C o m  p u ter Mod e l in g i n                                                                                                                            T                                                                                                                                                                                                   PressechScience
                  Engineering & Sciences


https://doi.org/10.32604/cmes.2026.082021

ARTICLE

Resilient     Federated     Ensemble     Learning     for     IoT     Intrusion     Detection     in
Adversarial      and      Imbalanced      Environments

Arvind    Prasad1, *,IbrahimAljubayri2,         Mohammad    Zubair    Khan3, *     and    Abdulfattah    Noorwali4


1Department    of    Computer    Engineering    &    Applications,    GLA    University,    Mathura,    India
2 Department   of   Computer   Science   and   Information,   Imam   Mohammad   Ibn   Saud   Islamic   University   (IMSIU),   Riyadh,   Saudi   Arabia
3Faculty    of    Computer    and    Information    Systems,    Islamic    University    of    Madinah,    Medina,    Saudi    Arabia
4 Electrical    Engineering    Department,    Umm    Al-Qura    University,    Makkah,    Saudi    Arabia

*Corresponding    Authors:    Arvind    Prasad.    Email:    arvind.prasad@gla.ac.in;    Mohammad    Zubair    Khan.    Email:
zubair.762001@gmail.com
Received:    11    March    2026;    Accepted:    18    May    2026;    Published:    30    June    2026

ABSTRACT:         Intrusion      detection      in      large-scale      IoT      deployments      becomes      particularly      challenging      during      ongoing
attack        scenarios,        where        malicious        traffic        may        temporarily        dominate       benign        traffic.        In        such        conditions,       streaming
network     data     exhibits     severe     class     imbalance     in     favor     of     attack     traffic,     while     device     behavior     remains     heterogeneous,
non-identically     distributed     (non-IID),     and     temporally     evolving.     Within     federated     learning     environments,     this     imbal-
ance        can        destabilize        early        aggregation        rounds,        dominant        attack        gradients        bias        the        global        model,        distort        decision
boundaries,      and      degrade      reliable      discrimination      of      residual      benign      behavior.      Since      the      server      has      no      access      to      raw
data,      these      effects      can      persist      across      communication      rounds      if      not      addressed      at      initialization.      This      article      addresses
the      problem      of      distributed      intrusion      detection      in      streaming      IoT      networks      under      severe      class      imbalance      and      partial
adversarial      behavior.       In      ongoing      attack      scenarios,      malicious      traffic      may      dominate      streaming      observations,      creating
an       inverted       imbalance       where       benign       behavior       becomes       underrepresented.       To       mitigate       these       issues,       we       propose       a
resilient    federated    ensemble    framework    with    three    key    components:    a    similarity-guided    balancing    phase    that    selects    a
structurally    diverse    subset    of    majority-class    samples    to    form    a    balanced    initialization    dataset,    an    incremental    ensemble
composed    of    Bernoulli    Naïve    Bayes,    Passive–Aggressive,    and    SGD    classifiers    for    pre-training    over    this    data    to    produce
a   warm-start   global   model,   and   an   accuracy-gating   mechanism   that   accepts   only   performance-preserving   local   updates
during     online     training.     The     proposed     approach     is     evaluated     on     flow-level     data     from     the     CICIoT2023     benchmark     that
demonstrated      stable      client-wise      convergence      with      high      accuracy      and      consistent      minority-class      discrimination,      even
under       skewed       attack-dominant       distributions.       Under       complete       label-flipping       poisoning,       corrupted       updates       are       sys-
tematically    rejected,    preventing    global    degradation.    Ablation    analysis    confirms    that    removing    structured    initialization
significantly     increases     early     instability.     The     results     indicate     that     balanced     global     conditioning     and     selective     federation
are    critical    for    maintaining    detection    reliability    in    streaming    IoT    systems    operating    under    sustained    attack    conditions.

KEYWORDS:   Federated   learning;   IoT   intrusion   detection;   streaming   analytics;   class   imbalance;   adversarial   robustness


1Introduction
         The     Internet     of     Things     (IoT)     is     now     pervasive,     with     billions     of     devices     and     sensors     operating     in     smart
homes,   industry,   healthcare,   and   cities   [1].   In   the   past   few   years   alone,   the   number   of   IoT   devices   has   increased
considerably,       resulting       in       a       large       growth       of       cyber       attacks.       Many       IoT       endpoints       are       low-cost       and       under-
protected,       so       they       enlarge       the       attack       surface       (botnets,       malware,       ransomware,       etc.).       IoT       network       traffic       is



Copyright    ©    2026    The    Authors.       Published    by    Tech    Science    Press.    This    work    is    licensed    under    a    Creative    Commons    Attribution    4.0    International
License,   which   permits   unrestricted   use,   distribution,   and   reproduction   in   any   medium,   provided   the   original   work   is   properly   cited.
```


### PDF page 2

[View original page, figures and tables](assets/page-002.png)

```text
2                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        Comput   Model   Eng   Sci.    2026;147(3):48


extremely       imbalanced       [2].       Client       data       are       heterogeneous       and       non-identically       distributed       (non-IID).       One
smart   camera’s   traffic   (e.g.,   home   surveillance)   can   be   very   different   from   a   temperature   sensor.   Clients   collect
different      volumes      of      data      and      different      feature      patterns.      In      practice,      this      means      a      single      global      model      must
reconcile     many     local     distributions.     In     this     context,     intrusion     detection     systems     (IDS)     are     essential.     IDS     has
acquired     a     key     role     in     defending     IoT     environments     [3].     Monitoring     the     high-volume     streams     of     IoT     data     is
critical    because    the    continuous    increase    in    cyber    attacks    makes    automated    defense    a    necessity    [4–6].
          Traditional         IDS         designs         assume         stable         traffic         and         centralized         visibility,         whereas         IoT         environments
are       highly       heterogeneous       and       continuously       evolving       [7].       Device       behavior       varies       across       deployment       con-
texts,         firmware         states,         workloads,         and         attack         conditions,         resulting         in         non-IID         and         temporally         drifting
traffic    distributions.
          Streaming     IoT     traffic     further     complicates     intrusion     detection     because     data     arrives     continuously     under
low-latency     constraints     [8].     Models     must     therefore     support     incremental     adaptation     while     remaining     robust
to    concept    drift,    evolving    device    behavior,    and    emerging    attacks.
          A         major         challenge         in         sustained         IoT         attack         scenarios         is         inverted         class         imbalance,         where         malicious
traffic       temporarily       dominates       benign       communication       (attack   >>       benign)       [9].       During       large-scale       attacks,
streaming       data       becomes       attack-heav y,       causing       optimization       to       be       dominated       by       malicious       gradients       and
biasing      decision      boundaries      toward      attack      patterns.      In      federated      environments,      these      effects      are      amplified
because     the     server     aggregates     model     updates     without     direct     visibility    into     class     distributions     [10,11].
          In    sustained    attack    scenarios,    the    local    class    prior    may    satisfy   P( y   =     1)≫P( y   =     0),where     y   =     1    denotes
malicious        traffic        and        y   =     0        benign        traffic.        Under        such        skew,        the        learning        objective        becomes        dominated
by      gradients      from      the      majority      attack      class,      shifting      the      decision      boundary      toward      malicious      regions      and
weakening   recognition   of   minority   benign   behavior.   In   federated   settings,   this   effect   can   be   amplified   because
theserverobservesmodelupdatesratherthantheunderlyingclassdistributions.
          Federated      Learning      (FL)      is      often      suggested      for      IoT      to      save      bandwidth      and      protect      privacy      [12–14].      In
FL,      the      devices      keep      their      raw      data      and      only      send      model      updates      to      a      central      server.      This      follows      privacy
laws     and     saves     data.     However,     since     the     server     never     sees     the     raw     data,     it     cannot     see     if     the     data     distribution
is     wrong.     The     server     just     combines     updates     from     many     different,     and     maybe     even     malicious,     devices.     Also,
communication    is    limited,    and    some    devices    might    go    offline.
          In         federated         IoT         intrusion         detection,         global         initialization         strongly         influences         early-round         stability
and      convergence      behavior      [15,16].     Under     attack-heav y     distributions,     poorly     conditioned     initialization     may
delay     reliable     discrimination     of     sparse     benign     traffic     and     amplify     instability     across     subsequent     communica-
tion     rounds.
          The     interaction     between     streaming     non-IID     traffic,     local     imbalance,     federated     aggregation     constraints,
and    adversarial    behavior    creates    a    cascading    instability    effect    during    deployment     [17–19].     The     overall     attack
and    instability    pathway    is    summarized    in     Fig.    1.
          As        shown        in       Fig.    1,       heterogeneous       IoT       clients       generate       skewed       local       updates       under       class       imbalance
and      temporal      drift.      These      updates      are      aggregated      without      access      to      raw      data,      which      can      amplify      majority-
class     dominance     during     early     rounds.     The     resulting     unstable     initialization     suppresses     rare     attack     gradients,
reinforces        bias        across        clients,        and        delays        detection        of        zero-day        activity,        thereby        expanding        the        security
exposure     window     during     ramp-up.
```


### PDF page 3

[View original page, figures and tables](assets/page-003.png)

```text
Comput   Model   Eng   Sci.    2026;147(3):48                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    3






























Figure   1:      Detailed  attack  propagation  and  instability  mechanisms  in  federated  IoT  intrusion  detection  under  streaming,
non-IID,    and    imbalanced    conditions.

           These   challenges   become   more    severe   in   the   presence    of   adversarial   behavior   such   as   poisoning   or   label-
flipping       attacks.       Existing       defenses       typically       assume       a       reasonably       stable       initial       model       [20].       Consequently,
poorly       conditioned      initialization      can      amplify      both      natural      non-IID      effects      and      malicious      client      influence
during    early    federated    rounds    [21–24].
           In    this    work,    we    propose    a    resilient    federated    ensemble    learning    method    for    IoT.    We    focus    on    cases    with
attacks      and      imbalanced      data.      We      do      not      try      to      solve      every      problem,      but      we      focus      on      how      streaming      data,
imbalance,     and     limited     coordination     affect     the     stability     of     the     early     model.     Our     goal     is     to     make     the     system
work     in    the    real    world,     not    just    in    theory.
           The     main     contributions     of     this     paper     are     summarized     as     follows:
•                                  A      similarity-guided      balancing      mechanism      that      selects      structurally      diverse      dominant-class      samples      to
           construct    a    balanced    and    information-rich    initialization    dataset.
•                                 A       cold-start-aware       federated       initialization       strategy       that       improves       early-round       stability       under       attack-
           heav y     IoT     traffic.
•                                 A         streaming         ensemble         learning         design         based         on         incremental         classifiers         for         continuous         adaptation
           without    full    retraining.
•                                 An      accuracy-gated      client      update      mechanism      that      rejects      poisoned,      noisy,      or      performance-degrading
           local     updates    before     aggregation.
•                                 A       unified       framework       that       jointly       addresses       imbalance,       non-IID       streaming       learning,       and       adversarial
           robustness    in    federated     IoT    intrusion    detection.
•                                 Experimental   validation   through   client-wise   analysis,   sensitivity   studies,   poisoning   experiments,   FGSM
           rejection     tests,     and     ablation     results.
```


### PDF page 4

[View original page, figures and tables](assets/page-004.png)

```text
4                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        Comput   Model   Eng   Sci.    2026;147(3):48


         The      remainder      of      this      paper      is      organized      as      follows.   Section    2     reviews      existing      literature      on      federated
intrusion         detection,         class         imbalance         mitigation,         streaming         learning,         and         adversarial         robustness         in         IoT
environments.    Section    3    presents    the    proposed    resilient    federated    intrusion    detection    framework.    Section    4
describes       the       experimental       setup       and       evaluates       the       proposed       approach       through       client-wise       performance
analysis,        poisoning        attack        experiments,        and        ablation        studies.        Finally,        Section    5       concludes        the        paper        and
outlines    directions    for     future    research.

2RelatedWork
         Recent    research    has    explored    multiple    directions,    including    federated    learning,    class    imbalance    mitiga-
tion,    streaming    adaptation,   and    adversarial    robustness.    While    several    studies    report    high    detection    accuracy,
their      assumptions,      optimization      objectives,      and      deployment      settings      vary      significantly.      It      is      therefore      nec-
essary      to      examine      these      works      in      a      structured      manner      to      understand      the      practical      limitations      that      remain
unresolved,     particularly     under     streaming     and    attack-dominant    traffic     conditions.     The     following     subsections
categorize     the     literature     accordingly.

2.1        Federated    Learning    for    IDS    on    CICIoT2023
         Abid       et       al.       [25]      proposed      a      hybrid      intrusion      detection      system      for      IoT      environments      combining      Grey
Wolf     Optimization    (GWO),     LightGBM,    and    a     CNN     classifier.    GWO    performs     wrapper-based     feature     selec-
tion       to       reduce       dimensionality.       LightGBM       generates       leaf-index       representations       through       gradient-boosted
trees,      which      are      embedded      and      processed      by      a      Conv1D-based      CNN      for      final      classification.      The      system      is
evaluated    on    the    CICIoT2023    and    CICIoMT2024    datasets.    The    authors    report    improved    detection    accuracy,
reduced          false          alarm          rates,          and          enhanced          computational          efficiency          compared          to          standalone          RF,          SVM,
DNN,       LSTM,       CNN,       and       attention-based       models.       The       approach       is       designed       for       deployment       in       fog-layer
IoT       architectures.       The       authors       achieved       an       average       accuracy       of       87.93%.       A       wrapper-based       dimensionality
reduction     using     GWO     and     efficient     leaf-wise     boosting     from     LightGBM     was     implemented,     which     achieved
high   performance   on   a   reduced   feature   space   (18   features   for   CICIoT2023,   5   for   CICIoMT2024)   and   achieved
improved     computational    efficiency    for    fog-layer    deployment.
         To  r  r  e           e  t           a  l  .           [26]      proposed      a      federated      learning-based      intrusion      detection      system      (IDS)      for      IoT      envi-
ronments     implementing     a     1D     CNN,     with     explicit     integration     of     three     privacy-preserving     (PP)     mechanisms:
Differential     Privacy     (DP),     Diffie–Hellman     (DH)     key     exchange,     and     Fully     Homomorphic     Encryption     (FHE).
The    proposed     approach    is    evaluated    on    TON-IoT,     IoT-23,     BoT-IoT,     CIC    IoT    2023,     CIC    IoMT    2024,     RT-IoT
2022,      and      EdgeIIoT.      Empirical      results      indicate      strong      predictive      performance      with      limited      computational
overhead         when         PP         layers         are         enabled.         The         study         emphasizes         operational         feasibility         rather         than         purely
theoretical      guarantees,      and      includes      convergence,      timing,      and      comparative      analyses.      The      rich      feature      sets
used       Network       traffic       features       extracted       from       CSV/PCAP-derived       flow       records,       including       protocol-based,
behavioral,     telemetry,     and     IoT     device     communication     attributes.     The     main     operational     advantage     is     layered
privacy      integration      within      FL.      The      simultaneous      use      of      DP,      DH      exchange,      and      FHE      is      uncommon      in      IDS
literature.        The        approach        reduces        exposure        of        raw        gradients        and        model        parameters        during        aggregation.
Empirically,      privacy      enforcement      adds      only      10%      computational      overhead,      which      is      relatively      modest      given
the    cryptographic    operations    involved.    Cross-dataset    validation    improves    external    validity.
         Okey      et      al.      [27]      presented      RAID-KL,      a      hybrid      KL–JS      knowledge      distillation      framework      for      resource-
aware   IoT   intrusion   detection   using   1D   CNN   teacher–student   models,   adaptive   temperature   scaling,   SMOTE
balancing,andSHAPexplanationsonCICIoT2023,CICIoMT2024,and.Theformulationismathematically
coherent,     and     the     experimental     scope     is     reasonably     broad.     However,     several     core     elements     need     tightening:
```


### PDF page 5

[View original page, figures and tables](assets/page-005.png)

```text
Comput   Model   Eng   Sci.    2026;147(3):48                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    5


hyperparameter   justification   is   weak,   resource   measurements   lack   methodological   clarity,   and   ablation   depth
is     insufficient     to     isolate    the     hybrid     loss     contribution.

2.2        Class    Imbalance    in    Intrusion    Detection    on    CICIoT2023
          Wa  h  a  b            e  t            a  l  .            [28]       proposed       an       optimized       CNN,       DNN,       and       Transformer       architectures       that       mitigate
class         imbalance         issues         through         SMOTE-based         oversampling         applied         strictly         to         training         folds         to         avoid
leakage.      Log      normalization      and      Min–Max      scaling      stabilize      feature      variance      before      balancing.      Empirically,
balancing         significantly         improved         recall         for         minority         classes,         especially         in         the         12-class         setting.         Without
rebalancing,      preliminary      experiments      showed      biased      decision      boundaries      favoring      high-frequency      DDoS
floods.   However,   synthetic   oversampling   introduces   risks   of   overfitting,   particularly   in   highly   sparse   minority
distributions.        Lightweight        CNN/DNN        configurations        adapted        for        IoT        resource        constraints.        The        authors
selected     feature     categories     such     as     statistical     network     flow     features,     time-based     traffic     features,     and     packet-
based   characteristics.   The   authors   reduced   the   features   from   the   original   46   features   to   37   meaningful   features
after    preprocessing.
          Mallikarjun         and         Patro         [29]        addressed        imbalance        issues        in        the        CICIoT2023        dataset        by        introducing
ZeroDefense,      focusing      on      detecting      emerging      zero-day      threats.      The      authors      implemented      SMOTE      during
supervised      training      that      limits      overfitting      to      minority      data      and      preserves      sensitivity      to      minority      behavior,
which,        in        practice,        often        resembles        zero-day        activity.        The        authors        identified        46        statistical        network        flow
features    extracted    from    IoT    traffic    (rate,    timing,    and    protocol-level    statistics)    for    detection.    Robust    handling
of    extreme    class    imbalance    without    collapsing    minority-class    recall,    achieved    through    a    cautious    separation
of     anomaly     screening     and     SMOTE-balanced     supervised     learning.
          Wakili       and       Bakkali       [30]       addressed       class       imbalance       in       the       CICIoT2023       dataset       by       proposing       a       SVM
Weights-based      Synthetic      sampling      (SVWS)      mechanism      that      generates      boundary-aware      synthetic      samples
rather       than       uniform       oversampling.       This       approach       concentrates       on       minority       augmentation       near       decision
margins,   reducing   overfitting   risks   observed   with   SMOTE-like   methods.   Combined   with   an   MLP   probability
feature   extractor   and   categorical   boosting   classifier,   the   framework   stabilizes   learning   under   skewed   distribu-
tions.    Integrated    probabilistic    feature    transformation     (MLPP)    improves    categorical    boosting    discrimination.
The      statistically     significant     improvements      were      validated      via      a      paired      t-test      and      the      Wilcoxon      signed-rank
test.     The     authors     used     features     categories     such     as     Flow-based     features     (flow     duration,     rate,     srate,     drate),     TCP
flag     statistics     (syn,     ack,     fin,     rst,     urg     counts),     Protocol     indicators     (HTTP,     HTTPS,     DNS,     TCP,     UDP,     etc.),     and
Statistical     features     (mean,     variance,     covariance,     IAT,     magnitude,     total     size,     total     sum).

2.3        Streaming    and    Incremental    Learning    for    Network    Security    on    CICIoT2023
          Wa  n  g            e  t            a  l  .            [31]        proposed        CTWA,        an        incremental        learning        framework        integrating        a        Convolutional
Autoencoder        (CAE)        and        a        Temporal        Convolutional        Network        (TCN)        for        IoT        intrusion        detection        under
streaming    conditions.    On    CICIoT2023,    initial    classes    (Benign,    DDoS-ACK,    DNS,    DDoS-ICMP)    are    trained
first,         followed         by         incremental         addition         of         new         DDoS         categories.         A         Gaussian-based         task         discriminator
and      Weight      Alignment      (WA)      mitigate      catastrophic      forgetting.      Feature      fusion      combines      spatial      (CAE)      and
temporal        (TCN)        representations.        Label        smoothing        is        integrated        with        cross-entropy        to        stabilize        updates.
Empirically,     CTWA    achieves    0.9643     accuracy    after    100     epochs     while    maintaining    the     old     task    performance,
though       with       non-trivial       runtime       overhead       (789.58       s)       The       integration       of       CAE       (spatial       compression)       with
TCN     (causal     dilated     temporal     modeling)     allows     simultaneous     structural     and     sequential     feature     extraction.
Residual      connections      reduce      gradient      degradation      in      deeper      CAE      layers.      The      Gaussian      task      discriminator
provides          a          probabilistic          routing          mechanism,          which          in          practice          reduces          interference          between          old          and
new        classes.        WA        partially        corrects        classifier        bias        across        task        heads.        Empirically,        forgetting        is        controlled
```


### PDF page 6

[View original page, figures and tables](assets/page-006.png)

```text
6                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       Comput   Model   Eng   Sci.    2026;147(3):48


without       explicit       exemplar       replay.       The       types       of       features       used       for       detection       are       46-dimensional       flow-level
statistical     features.
          Mahdi      et      al.      [32]     proposed     an     end-to-end     intrusion     detection     framework     integrating     streaming     incre-
mental       learning       with       secure       data       lifecycle       management.       An       SGD-based       incremental       classifier       is       initially
trained      on      CICIoT2023      and      subsequently      updated      using      traffic      data      extracted      from      a      blockchain-secured
storage         layer.         The         model         supports         partial_fit         retraining,         avoiding         full         retraining         cycles.         Data         collected
from       live       traffic       is       encrypted       (hybrid       AES/RSA   +       signature),       stored       via       Proof-of-Work       blockchain,       then
periodically       retrieved       for       incremental       updates       on       a       central       server.       Retraining       occurs       in       multiple       rounds,
improving     cross-validation     accuracy     from     97.9%     to     99.8%.     The     approach     addresses     resource     constraints     in
IoT    devices    while    maintaining    model    adaptability    to    evolving    attack    distributions.

2.4        Adversarial    Robustness    in    Federated    Learning    on    CICIoT2023
          Doménech      et      al.      [33]      evaluated      adversarial      robustness      through      cross-domain      generalization      between
CICIoT2023   and   CICIoMT2024.   Models   trained   on   CICIoT2023   show   strong   baseline   performance,   but   sub-
stantial    degradation    when    evaluated    on    IoMT    traffic,    even    under    equivalent    attack    categories.    The    proposed
approach      demonstrates      systematic      cross-domain      generalization      analysis      between       IoT      and      IoMT      datasets.
The   experimental   result   shows   that   minor   IoMT   augmentation   significantly   restores   detection   capability.   The
authors    achieved    99.85%    accuracy    after    a    controlled    optimization    pipeline.    The    results    suggest    CICIoT2023-
trained     models     are     not     inherently     adversarially     robust     to     domain     shifts    in     healthcare     environments.
          Saxena       et       al.       [34]       proposed       GNN-IDS,       a       Graph       Neural       Network-based       IDS       that       was       experimented
on           the           CICIoT2023           dataset.           The           proposed           approach           emphasizes           on           structural           modeling           of           network
traffic.       Unlike       traditional       ML       approaches       that       operate       on       independent       flows,       the       proposed       method       con-
structs         a         graph         using         node         and         edge         attributes,         allowing         relational         reasoning         across         IoT         entities.         The
proposed        approach’s        advantage        lies        in        explicit        graph        construction        using        both        node        and        edge        attributes.
The       GraphSAGE-based       architecture       leverages       relational       dependencies       across       IoT       entities,       mitigating       the
independence       assumption       common       in       flow-based       classifiers.       Binary       accuracy       (99.95%)       exceeds       baseline
models      (FedFK,      RF,      MLP-Mimic).      The      model      demonstrates      high      precision      across      most      attack      categories,
particularly     DoS     and     DDoS     subclasses.
          To       better       understand       how       existing       studies       address       intrusion       detection       in       IoT       environments,        Ta  b  l  e        1
provides     a     structured     comparison     of     recent     works     evaluated     on     CICIoT2023     and     related     datasets.     The     table
summarizes    their    feature    selection    strategies,    learning    paradigms,    key    strengths,    and    practical    limitations—
particularly     in     terms     of     federated     learning,     streaming     capability,     class     imbalance     handling,     and     robustness.
This     comparison     helps     highlight    the     gaps     that     motivate    the     proposed     framework.

                                             Ta  b  l  e       1  : Comparative    analysis    of    recent    IDS    research    on    CICIoT2023.

       Authors                          Feature                    Model/Learning                                                                                        Critical    Limitations
         (Year)                       Selection                          Paradigm                                                                                       Key    Advantages(W.r.t.    FL,    Streaming,
                                                                                                                                                                     Imbalance,    Robustness)
                                                                                                                         Significant                                   No    federated     learning;
                                          GWO                               Hy brid                      dimensionality    reduction                                   offline    evaluation    only;
           Abid                      (Wrapper-                        LightGBM  +                        (43  →18);    low    false    alarm                        degraded     minority    attack
      et     al.    [25]                 based)                               CNN                         rate;    strong    detection    for                         detection;     no    streaming
                                                                                                                  dominant     attacks                               capability;    no    adversarial
                                                                                                                                                                           robustness     analysis
                                                                                                                                                                                                  (Continued)
```


### PDF page 7

[View original page, figures and tables](assets/page-007.png)

```text
Comput   Model   Eng   Sci.    2026;147(3):48                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    7


Ta  b  l  e        1        (  c  o  n  t  i  n  u  e  d  )

      Authors                        Feature                  Model/Learning                                                                                 Critical    Limitations
         (Year)                    Selection                       Paradigm                                                                                       Key    Advantages(W.r.t.    FL,    Streaming,
                                                                                                                                                         Imbalance,    Robustness)
                                                                   1D-CNN+                              Privacy-preserving                                No    imbalance    handling;
         To  r  r  e                                                Federated                        federated     framework;                            no     poisoning     defense;     no
      et    al.    [26]                                                                           NoneAveraging  +asynchronous     FL;                     streaming     incremental
                                                                   DP  +    FHE                      evaluated    on    multiple                          updates;     computational
                                                                                                        large-scale    datasets                                   overhead     (10%)
                                                                   1D-CNN+                                   91.24%     model                           Centralized    training    only;
                                                                  Knowledge                                  compression;                                no     federated     learning;     no
          Okey                         Firefly                    Distillation                             resource-aware                                    streaming     setting;     no
      et    al.    [27]            Algorithm                        (Teacher–                       deployment;     SMOTE  +                                adversarial    robustness
                                                                     Student)                                weighted    loss;                                         evaluation
                                                                                                  explainability    integration
                                                                                                                                                          Evaluated     on     3M     subset
                                   Variance-                                                         High    binary    accuracy;                             (not    full    dataset);    no
        Wa  h  a  b                    based                     DNN/CNN/                               SMOTE    balancing;                                    federated     learning;
      et     al.    [28]             pruning                     Tr  a n s  f o r  m  e  r           multi-class     evaluation                              performance    drop    in
                                                                                                                                                               12-class    setting;    no
                                                                                                                                                               robustness     analysis
                                                                                                           Effective     severe                         Binary     classification     only;
   Mallikarjun                       Implicit                    MLPP-CB  +                       imbalance    handling;    very                            centralized    setting;    no
   &Patro[29]                      (CatBoost                           SVWS                        high    attack    recall;    stable                     streaming    learning;    no
                                 importance)                        balancing                              cross-validation                               federated     paradigm;    no
                                                                                                              performance                                    adversarial    resilience
                                       None                           Hy brid                           Zero-day    detection                            Centralized     architecture;
      Wa  k  i  l  i        &       (implicit                   anomaly-first                          capability;    macro-F1                           no     federated     learning;     no
   Bakkali    [30]                    feature                   cascade    (IF  +                            improvement;                                streaming    adaptation;    no
                                    learning)                    AE  +     LOF  +                    edge-deployable     (<100                                 poisoning     defense
                                                                    RF/XGB)                                  ms     inference)
                                                                                                     Mitigates    catastrophic                             No    federated     learning;
                                   Automat ic                     Incremental                          forgetting;     supports                               high    computational
         Wa  n  g                 (CAE-TCN                     Deep     Learning                           unknown     attack                               runtime;    evaluated    on
      et     al.    [31]              feature                        (CTWA)                               detection;    hybrid                          relatively    balanced    subset;
                                  extraction)                                                             temporal-spatial                                    no     adversarial     study
                                                                                                                 modeling
                                                                                                                                                                                    (Continued)
```


### PDF page 8

[View original page, figures and tables](assets/page-008.png)

```text
8                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       Comput   Model   Eng   Sci.    2026;147(3):48


Ta  b  l  e        1        (  c  o  n  t  i  n  u  e  d  )

       Authors                         Feature                    Model/Learning                                                                                      Critical    Limitations
         (Year)                      Selection                         Paradigm                                                                                       Key    Advantages(W.r.t.    FL,    Streaming,
                                                                                                                                                                 Imbalance,    Robustness)
                                     ML-based                                                             Continuous    retraining;                                Central    retraining    only;
         Mahdi                          feature                      Incremental                             secure     data     storage;                        no     federated     learning;     no
      et     al.    [32]              selection                           SGD  +                            validation     on     unseen                                explicit    imbalance
                                      (unspeci-                       Blockchain                                         datasets                                  strategy;     no     adversarial
                                           fied)                                                                                                                     robustness     evaluation
                                                                                                         Quantified    dataset    shift                          No     federated     learning;     no
    Doménech                                                                                             (F1    drop     up     to    66.87%);                   streaming;    no    adversarial
      et    al.    [33]                                                                            None                                                       Random    Forest+     SMOTEoptimized    preprocessing;robustness;     limited
                                                                                                       domain-aware    evaluation                                      cross-dataset    scope
                                                                   GraphSAGE  +                              Captures    structural                                   We  a  k        m  i  n  o  r  i  t  y  -  c  l  a  s  s
        Saxena                                                              MLP                         dependencies;     improved                                 precision;    no    imbalance
      et    al.    [34]                                                                           None(GNN-basedtopology-aware     intrusion                         analysis;    no    federated
                                                                             IDS)                                      detection                                    learning;    no    streaming
                                                                                                                                                                                 capability


         In    summary,    existing    studies    generally    optimize    one    aspect    of    IoT    intrusion    detection,    such    as    privacy-
preserving     federation,     imbalance     handling,     streaming     adaptation,     or     adversarial     defense.     Limited     attention
has   been   given   to   their   joint   interaction   under   sustained   attack-dominant   and   non-IID   streaming   conditions.
Thisgapmotivatestheintegratedframeworkproposedinthiswork.

3         Proposed     Approach
         This        section        presents        the        proposed        federated        intrusion        detection        framework        for        IoT        environments
operating    under    adversarial     and    imbalanced    conditions.
         In     this     study,     resilience     denotes     the     ability     of     the     intrusion     detection     framework     to     preserve     stable     and
reliable      performance      under      non-IID      streaming      traffic,      severe      class      imbalance,      and      malicious      or      degraded
client    updates.
         The     overall     workflow     consists     of     feature     selection,     similarity-guided     initialization,     and     accuracy-gated
federated     ensemble     learning,     as     illustrated     in    Fig.    2.
         Similarity-Guided     Data     Balancing:    Majority-class     samples     are     analyzed     for     redundancy,     and     a     struc-
turally     diverse    subset    is    selected    to    construct    a    balanced    initialization    dataset.
         Robust      Global      Ensemble      Initialization:    An      incremental      ensemble      model      is      trained      on      the      balanced
dataset     to     obtain     a     stable,     cold-start     global     model.
         Streaming        Federated        Refinement        with        Accuracy        Gating:   Clientsprocesslocaldatainstreaming
batches,    perform    conditional    incremental    updates,    and    transmit    only    performance-preserving    updates.    The
server    aggregates    accepted    updates    using    performance-weighted    aggregation    under    secure    communication.
         Fig.    2      summarizes      the      complete      workflow      of      the      proposed      framework,      integrating      feature      reduction,
similarity-guided    initialization,    and    accuracy-gated    federated    refinement    under    streaming    IoT    conditions.
```


### PDF page 9

[View original page, figures and tables](assets/page-009.png)

```text
Comput   Model   Eng   Sci.    2026;147(3):48                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    9














































     Figure    2:        Overall    process    flow    of    the    proposed    resilient    streaming    federated    IoT    intrusion    detection    framework.

3.1        mRMR-Based    Feature    Selection    and    Importance    Analysis
           Feature    selection    plays    a    critical    role    in    intrusion    detection    systems    for    IoT    environments,    where    traffic
characteristics    are    high-dimensional    and    exhibit    strong    statistical    dependencies    [35–37].    To    identify    features
that    are    both    informative    with    respect    to    class    behavior    and    minimally    redundant,    this    work    employs    a    Max-
imum      Relevance      Minimum      Redundancy      (mRMR)-based      feature      selection      framework      on      the      CICIoT2023
dataset    [38].    The    original    CICIoT2023    dataset    contains    46    input    features    (excluding    the    label    attribute).    The
objectiveisnottorelysolelyonagreedyrankingorder,buttoobtainacompactanddiscriminativesubset
of     features    while    preserving     the    semantic    relevance     of    the    original    traffic     descriptors     [39,40].
           Let       D  ={(xi  ,     y i )}Ni=1   denote    the    preprocessed    dataset,    where   xi   ∈Rd      represents    a    d -dimensional    vector
of         normalized         network-flow         features         and          y i   ∈{0,   1}         corresponds         to         benign         and         malicious         IoT         traffic,
respectively.     Feature     relevance     is     quantified     using     mutual     information     between     an     individual     feature        f  j      and
the    class    label     Y  ,
```


### PDF page 10

[View original page, figures and tables](assets/page-010.png)

```text
10                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                Comput   Model   Eng   Sci.    2026;147(3):48



I(  f  j ;   Y)=   ∑p(  f  j ,     y)   log                  p(  f  j ,     y)p(  f  j) p( y),(1)
                   f  j , y

which    captures    the    expected     reduction     in    uncertainty    about     Y       provided     by      f  j .
        To    account    for    the    pronounced    correlation    structure    typical    of    IoT    traffic    statistics,    feature    redundancy
is     modeled     as     the     mean     absolute     Pearson     correlation     between       f  j      and    all    remaining    features,

                          d
R(  f  j)=                         1d  −1∑∣ρ(  f  j ,      f k)∣.(2)
                         k=1
                         k≠j

        The     raw     mRMR     feature     importance     score     is     then     computed     as

mRMR(  f  j)=         I(  f  j ;   Y)−R(  f  j).(3)

        Since     redundancy     may     dominate     relevance     in     highly     correlated     feature     spaces,     raw     mRMR     values     can
assume    negative    magnitudes.    To    enhance    interpretability    while    preserving    relative    importance    relationships,
all    scores    are    normalized     using    min–max    scaling    into    the    interval  [0,   1].
        While     performance-based     weighting     improves     contribution     from     reliable     updates,     high     local     accuracy
may     not     always     correspond     to     greater     global     usefulness     under     heterogeneous     non-IID     client     distributions.
In         particular,         clients         with         comparatively          easier         local         data         may         receive          stronger          influence         than         clients
representing    more    challenging    but    important    distributions.    This    trade-off    is    accepted    here    for    computational
simplicity    and    lightweight    deployment.
        The        analysis        is        performed        independently        for        benign        and        malicious        traffic        to        capture        class-specific
behavioral      characteristics.      Fig.    3      illustrates      the      normalized      mRMR      feature      importance      for      class      0      (benign
IoT     traffic).     Several     temporal     and     protocol-related     features     exhibit     consistently     high     importance,     indicating
their      role      in      characterizing      stable      and      regular      communication      patterns      typical      of      legitimate      IoT      behavior.
In         contrast,         statistical         dispersion         features,         such         as         minimum,         maximum,         and         variance-based         descrip-
tors,         demonstrate         comparatively         lower         importance,         suggesting         limited         discriminative         value         for         benign
traffic    modeling.





















       Figure    3:        Normalized    mRMR    feature    importance    for    class    0    (benign    IoT    traffic)    in    the    CICIoT2023    dataset.
```


### PDF page 11

[View original page, figures and tables](assets/page-011.png)

```text
Comput   Model   Eng   Sci.    2026;147(3):48                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 11


            Fig.    4         presents         the         corresponding         feature         importance         profile         for         class         1         (malicious         IoT         traffic).         In
this      case,      a      broader       set      of       features      achieves      elevated      importance      values,      reflecting       the      heterogeneous       and
irregular      nature      of      attack      traffic.      Notably,      features      associated      with      protocol      usage,      control      flags,      and      traffic
intensity         display         stronger         relevance,         indicating         their         effectiveness         in         capturing         deviations         from         normal
communication      behavior.      This      divergence      in      importance      patterns      highlights      the      asymmetric      information
content     between     benign     and     malicious     traffic     classes.





















        Figure    4:         Normalized    mRMR    feature    importance    for    class    1    (malicious    IoT    traffic)    in    the    CICIoT2023    dataset.

            To     identify    features    that    remain     consistently    informative    across    both    traffic    classes,    a    combined    feature
importance        profile        is        constructed        by        averaging        the        raw        mRMR        scores        from        class        0        and        class        1        prior        to
normalization.      The      resulting      distribution,      shown      in    Fig.    5,      emphasizes       features      that      contribute      robustly      to
discrimination     regardless     of     class     context.     These     features     are     particularly     well-suited     for     intrusion     detection
models    intended    for    deployment    in    dynamic    IoT    environments,    where    attack    patterns    and    benign    behaviors
may     evolve     over     time.





















Figure         5:        Combined         normalized         mRMR         feature         importance         across         benign         and         malicious         traffic         classes         in         the
CICIoT2023    dataset.
```


### PDF page 12

[View original page, figures and tables](assets/page-012.png)

```text
12                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                Comput   Model   Eng   Sci.    2026;147(3):48


          For    subset    construction,    the    combined    normalized    mRMR    scores    were    sorted    in    descending    order,    and
a      fixed      retention      ratio      of      80%      was      applied.      Based      on      this      criterion,      the      top      80%      highest-scoring      attributes
were   retained   for   subsequent   experiments,   while   lower-ranked   features   were   discarded.   This   process   reduced
the     original     46-dimensional     feature     space     to     31     selected     features,     improving     computational     efficiency     while
preserving    discriminative    information    relevant    to    IoT    intrusion    detection.
          Fig.    6     shows     the     final     selected     feature     subset     used     for     federated     model     training.     The     retained     attributes
include     protocol     indicators     (e.g.,     ARP,     DHCP,     DNS,     SSH,     Telnet,     SMTP),     traffic-rate     descriptors     (e.g.,     Rate,
Srate),   temporal   flow   properties   (e.g.,   Duration,   flow_duration),   and   TCP   control-flag   statistics   (e.g.,   ack,   syn,
rst,    fin,    cwr,    ece).    This    distribution    indicates    that    both    protocol    semantics    and    traffic    behavior    are    important
for    reliable     detection    in    dynamic    IoT    environments.


























Figure       6:         Final        selected        feature        subset        with        normalized       mRMR        scores        used        in        the        proposed        federated        intrusion
detection    framework.

          The     mRMR     framework     was     therefore     used     not     only     for     feature     importance     interpretation,     but     also     to
guide     feature     reduction     and     construct     a     consistent     input   space    shared    across    all    clients    and    all    experiments.

3.2        Similarity-Guided    Data    Balancing    for    Robust    Global    Initialization
          A    fundamental    challenge    in    federated    and    streaming    intrusion    detection    systems    lies    in    the    simultane-
ous    presence    of    severe    class    imbalance    and    cold-start    instability    during    global    model    initialization    [41,42].    In
large-scale   network   telemetry   datasets,   malicious   traffic   (class   1)   often   dominates   benign   instances   (class   0)   by
several     orders     of     magnitude,     biasing     both     centralized     and     federated     learners     toward     majority-class     decision
boundaries.      When      such      an      imbalance      is      propagated      into      federated      environments,      the      initial      global      model
becomes   poorly   conditioned,   leading   to   unstable   early   updates,   delayed   convergence,   and   degraded   detection
accuracy         [43].         To         address         this         issue,         we         propose         a         similarity-guided         balancing         strategy         that         performs
principled       majority-class       reduction       while       preserving       behavioral       diversity,       thereby       enabling       robust       global
initialization    and    mitigating    cold-start     effects.
```


### PDF page 13

[View original page, figures and tables](assets/page-013.png)

```text
Comput   Model   Eng   Sci.    2026;147(3):48                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               13


           To          formalize          the          imbalance          setting          considered          in          this          study,          the          dominant          and          minority          traffic
distributions     are     defined     as     follows.
           Let              D1 ={x(1)i        }N1i=1       denote        the        set        of        dominant-class        samples        (class        1,        malicious        traffic),        where        each
x(1)i           ∈Rd          represents        a        d -dimensional        feature        vector        derived        from        network        traffic        statistics.       Similarly,        let
D0  ={x(0)j         }N0j=1    denote     the     underrepresented-class     dataset    (class     0,     benign     traffic),     with   N1  ≫N0 .
           In      ongoing      attack      scenarios,      streaming      traffic      becomes      attack-heav y,      causing      benign      communication
patterns      to      appear      sparsely      [44].      Under      such      an      inverted      imbalance,      gradient-based      optimization      is      dom-
inated         by         malicious         gradients,         suppressing         benign         structure         and         biasing        early         decision         boundaries.         To
prevent    benign-class    underrepresentation    during    initialization,    the    objective    is    to    construct    a    reduced    subset
D1  ⊂˜      D1    such     that  ∣D1∣=˜                  N0 ,     yielding     a     balanced     dataset

Dbal    =           ˜D1 ∪D0 ,

while    preserving     structurally     diverse     malicious    behaviors.
           To    achieve    this,    we    quantify    the    intrinsic    redundancy    of    dominant-class    (malicious)    samples    through    a
similarity-based     functional.     Let      ϕ(x)∈Rd       denote     the     normalized     representation     of     a     sample     after     numeric
feature    sanitization.    For    any    two     dominant-class    samples    x(1)i                      and    x(1)j               ,     we     define     a     similarity     kernel

S(x(1)                                            ϕ(x(1)i       )−ϕ(x(1)j       )∥2                  ,(4)
         i                 ,   x(1)j      )=     1−∥max ϕ(x(1)                 ϕ(x(1)
                                             k , l      ∥k     )−                       l        )∥2

which        maps        pairwise        Euclidean        distances        into        a        bounded        similarity        score        in    [0,   1].Highervaluesof                                           S
indicate         greater         redundancy         within         the         attack         manifold,         while         lower         values         correspond         to         structurally
distinct     malicious     behaviors.
           For       each      dominant-class      instance      x(1)i                 ,       we       compute       an       aggregate       similarity       score       with       respect       to       the
entire     dominant-class     distribution:

                                        N1
ψ(x(1)i      )=                              1N1 −1∑S(x(1)i                 ,   x(1)j       ).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              (5)
                                        j=1
                                       j≠i

           The       scalar    ψ(x(1)i        )      serves       as       a       redundancy       measure:       samples       with       high      ψlie       in       dense       regions       of       the
malicious    manifold,    whereas    samples    with    low    ψcapture     diverse     attack     behaviors     that     are     more     informative
for    discriminative    learning.
           The         pairwise         similarity         computation         has         quadratic         complexity         with         respect         to         the         dominant-class
sample    count,    i.e.,        O(N  21 ).    However,    this    operation    is    performed    only    once    during    the    server-side    initializa-
tion      stage      and      is      not      repeated      during      subsequent      federated      communication      rounds.      Therefore,      it      does      not
contribute    to    the    recurring    online    training    overhead.
           In      practical      deployments,      the      computation      can      be      accelerated      through      vectorized      matrix      operations,
multi-core         or         GPU-based         parallelization,         and         block-wise         distance         evaluation.         For         large-scale         datasets,
approximate           strategies           such           as           random           subsampling,           clustering-based           prototype           generation,           nearest-
neighbor       sparsification,       or       locality-sensitive       hashing       can       be       adopted       to       reduce       computational       cost       while
preserving     representative     structural     diversity     within     the     dominant     class.
```


### PDF page 14

[View original page, figures and tables](assets/page-014.png)

```text
14                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                Comput   Model   Eng   Sci.    2026;147(3):48


         The   dominant-class   dataset    D1   is    then    sorted    in    ascending    order    of   ψ(⋅),andonlythelowest        N0     samples
are     retained:
D1  =     arg                               min˜       6)
                A⊂D1,∣A∣=N0  ∑x∈A  ψ(x).(

         This    selection    criterion    ensures    that    malicious    samples    exhibiting    maximal    structural    diversity    are    pre-
served,    while    highly    redundant    attack    instances    are    systematically    discarded.    In    the    conducted    experiments,
this       procedure       reduced       the       original       dominant-class       dataset       to       match       the       cardinality       of       the       benign       class,
yielding        a        balanced        initialization        dataset.        Since        only        the        reduced        initialization        subset        is        required,        exact
evaluation     over     the     full     dominant-class     set     is     not     mandatory,     and     approximate     candidate     selection     methods
remain     suitable     in    large     deployments.
         Beyond   class   balance,   the   proposed   strategy   plays   a   critical   role   in   stabilizing   global   model   initialization.
Let      θ0       denote      the      parameters      of      the      initial     global      model      trained      on         Dbal  .Since          Dbal          is      both      balanced      and
diversity-preserving,     θ0      provides     a     well-conditioned     approximation     of    the     joint    class    distribution:

θ0   ≈arg   minθ                  E(x, y)∼Dbal   [L(  f θ(x),     y)],(7)

where           L(⋅)denotes      the      model-specific      classification      loss      (log-likelihood      for      Bernoulli      Naïve      Bayes,      hinge
loss     for     Passive–Aggressive,     and     logistic     loss     for     SGD).
         This          initialization          mitigates          the          cold-start          instability          commonly          observed          in          federated          streaming
learning,       wherein       early       updates       would       otherwise       be       dominated       by       attack-heav y       gradients       that       suppress
benign    discrimination.
         The           proposed           initialization           stage           reduces           attack-dominant           bias           by           constructing           a           balanced           and
diversity-preserving     training    subset    prior     to    federated    optimization.
         Empirically,   the   similarity-guided   balancing   approach   produces   a   reduced   yet   information-rich   training
set   that   improves   convergence   speed,   stabilizes   early   federated   updates,   and   preserves   benign-class   sensitivity
under       attack-dominant       streaming       conditions.       By       embedding       balancing       directly       into       global       initialization
through    a    mathematically    grounded    similarity    functional,    the    proposed    method    establishes    a    principled    link
between     dataset     conditioning     and     federated     robustness     in     adversarial     IoT     environments.

3.3        Proposed    Streaming    Federated    Learning    Framework    with    Robust    Global    Initialization
         This         section         presents         the         proposed         federated         intrusion         detection         framework         for         handling         attack-
dominant      imbalance,      cold-start       instability,      federated       privacy       constraints,      and      unreliable       client      updates       in
streaming     IoT     environments.
         The         proposed         streaming         federated         framework         is         designed         for         IoT         environments         characterized         by
non-IID        traffic        distributions,        attack-dominant        imbalance,        and        unreliable        client        updates        during        continu-
ous     operation.
Problem    Setting    and    Motivation
         Let        Dk  ={(x(k)i                    ,     y(k)i          )}N ki=1    denote    the    local    dataset    of    client      k,where     x(k)i            ∈Rd       represents     numeric     IoT
traffic     features     and      y(k)i          ∈{0,   1}      denotes      benign      (0)      or      attack      (1)      traffic.      In      sustained      attack      conditions,      the
local       class       distribution       typically       satisfies       N(1)k          ≫N(0)k                 ,       meaning       malicious       instances       dominate       streaming
observations     while     benign     traffic     becomes     underrepresented.
```


### PDF page 15

[View original page, figures and tables](assets/page-015.png)

```text
Comput   Model   Eng   Sci.    2026;147(3):48                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               15


          Under     an     attack-dominant     imbalance,     early     optimization     becomes     biased     toward     malicious     gradients,
weakening         benign-class         discrimination.         Since         federated         servers         do         not         access         raw         data,         this         bias         may
propagate    across    communication    rounds    if    initialization    is    poorly     conditioned.
          Classical      federated       learning      approaches      assume      reasonably       balanced      distributions       and       reliable       client
updates          [45].         However,         in         attack-heav y         streaming         IoT         environments,         poorly         conditioned         initial         mod-
els         amplify         benign-class         suppression,         while         corrupted         or         mislabeled         local         data—whether         accidental         or
adversarial—can     further     destabilize     aggregation.     These     effects     motivate     a     federated     design     that     is            cold-start
aware,    incremental     by     construction,and     selective     in     accepting     client     updates.
Similarity-Guided    Global    Initialization
          To          mitigate          cold-start          instability,          the          global          model          is          initialized          using          a          balanced          and          diversity-
preserving    dataset    constructed    via    the    previously    introduced    Similarity-Guided    Data    Balancing     mechanism.
          Let            D1      and           D0        denote      the      majority      (malicious)      and      minority      (benign)      class      datasets,      respectively.       A
similarity       functional       ψ(x)       is       computed       for       each       x  ∈D0 ,       capturing       redundancy       within       the       benign       feature
manifold.    The    balanced    initialization    set    is    defined     as
Dinit   =           ˜D0  ∪D1,where  ∣D0∣=∣˜                            D1∣.

          This         construction         preserves         structural         diversity         while         eliminating         redundant         benign         observations,
yielding    a    well-conditioned     dataset    for    initializing    the    global    model.
Incremental    Learning    as    a    First-Class    Design    Choice
          To         support         streaming         IoT         traffic         under         federated         constraints,         the         framework         adopts         incremental
learning    through    partial_fit-based    updates,    enabling    mini-batch    adaptation    without    full    retraining.
          Based          on          extensive          empirical          evaluation,          three          incremental          classifiers          were          selected          due          to          their
complementary     inductive     biases     and     superior     performance     on     the     CICIoT2023     datasets:
•                               Bernoulli    Naïve    Bayes    (BNB):    robust     to     sparse,     binary,     and     thresholded     traffic     indicators.
•                               Passive–Aggressive       Classifier       (PA):      margin-based       learner       capable       of       rapid       adaptation       to       emerging
          attack     patterns.
•                               Stochastic   Gradient   Descent   Classifier   (SGD):  scalable   linear   learner   with   probabilistic   loss   modeling.
Streaming    Federated    Learning    Protocol
          The     federated     learning     process     unfolds     in     two     operational     phases.
Phase     I:     Server-Side     Global     Initialization
          The     federated     server     initializes    an     ensemble     E0      by    incrementally     training    each    base    learner     on        Dinit :
θ(0)            partial_fit(θ(0)                                                   1,   2,   3}.
   m        ←                              m            ,      Dinit),                          m  ∈{

          Model    quality    is    evaluated    on    a    disjoint    evaluation    dataset    using    stratified    sampling,    allocating    20%    for
validation    and    20%    for    testing    while    preserving    the    original    class    distribution.    The    initialization    dataset   Dinit
is     never     reused     for     validation     or     testing.
Phase    II:    Accuracy-Gated    Streaming     Federated     Refinement
          When      a      client       k       connects,      it      retrieves      the      current      global      ensemble           Et        over      a      secure      HTTPS      channel.
Localdataareprocessedinstreamingbatchesofsize                              B  =     1000:

D(b)k         ={(x(k)i                    ,     y(k)i          )}Bi=1.
```


### PDF page 16

[View original page, figures and tables](assets/page-016.png)

```text
16                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                Comput   Model   Eng   Sci.    2026;147(3):48


         Before   performing   any   local   update,   the   client   evaluates   the   current   global   ensemble   on        D(b)k                     and   obtains
a     baseline     accuracy     Acc(b)global  .     The    client    then    tentatively     updates    its    local    copy     using    incremental    learning:

θ(t+1)            partial_fit(θ(t)
  m , k        ←                            m          ,      D(b)k        ).

         The    updated    local    ensemble    is    re-evaluated    on    the    same    batch,    yielding    Acc(b)local .    The    update    is    accepted
only     if

Acc(b)local   ≥Acc(b)global   −δ,

where      δisatolerancemargin(setto5%inexperiments).Ifthisconditionisviolated,thebatchupdateis
discarded,     and     a     diagnostic     message     is     generated.
         This     accuracy-gated     mechanism     prevents     harmful     updates     arising     from     label-flipped,     noisy,     or     adver-
sarial    data,    while    still    permitting    b enign    distributional    variation.
         Algorithm       1       summarizes       the       client-side       streaming       federated       procedure,       including       batch       evaluation,
temporary    incremental    learning,    and    the    accuracy-gated    update    acceptance    mechanism    under    non-IID    and
potentially     corrupted     local     data.
         The        algorithm        explicitly        separates        tentative        local        updates        from        committed        parameter        replacement,
thereby     preventing     propagation     of     performance-degrading     gradients    to     the    federation.
Performance-Weighted    Ensemble    Aggregation
         Accepted   client   updates   are   transmitted   to   the   server   as   model   parameters   accompanied   by   performance
statistics.      Model      parameters      are      aggregated      using      symmetric      parameter      averaging,      while      ensemble      voting
weights      are      updated      in      a      performance-proportional      manner.      This      hybrid      design      preserves      the      stability      of
parameter      fusion      while      allowing      reliable      client      contributions      to      influence      ensemble      decision      strength.      Let
f m(x)    denote     the     prediction     of     base     learner     m.Theensembledecisionisdefinedas

                      M                              1
y(x)=          I (ˆ  ∑                               2 )      ,
                    m=1 w m    f m(x)≥
where    the    weights    are    updated    as

w(t+1)m               =     w(t)m       +       Ac  c(b)k
                                     2                          ,
followed     by    normalization:

w(t+1)m               ←   w(t+1)m          .
                   ∑M
                        j=1  w(t+1)j

         Weight   normalization   prevents   unbounded   growth   across   federated   rounds   and   preserves   the   numerical
stability     of     the     ensemble     decision     threshold.
         In      the      experimental      evaluation,      the      default      client-side      tolerance      parameter      was      set      to      0.95      relative      to
the      current      server      accuracy,      corresponding      to      δ=     0.05,      while      the      server-side      acceptance      threshold      was      set
to    0.90.    Additional    sensitivity    analysis    was    conducted    using    alternative    client-side    thresholds    to    examine    the
trade-off    between    robustness    and    update    acceptance.    This    asymmetric    design    enforces    stricter    local    filtering
prior     to     a     comparatively     tolerant     global     aggregation     stage.
```


### PDF page 17

[View original page, figures and tables](assets/page-017.png)

```text
Comput   Model   Eng   Sci.    2026;147(3):48                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       17


Algorithm    1: Accuracy-gated     client-side     streaming     federated     update
Require:        Global         ensemble               E g  ={(M m  ,   w m)}Mm=1,         server         accuracy          Ac  c g ,localdataset         D k ,         batch         size         B,
        tolerance     δ
Ensure:    Accepted    local    model    updates    transmitted    to    server
   1:               Receive (E g  ,    Ac  c g)    from    server
   2:              Partition     D k       into     batches  {D(b)k        }Tb=1    of     size     B
   3:              for    each    batch     D(b)k         =(Xb  ,     yb)    do
   4:                                                //    Step    1:    Evaluate    current    global    ensemble
   5:                                                 Compute    weighted    ensemble    predictions:
                                             M                                             1
           y   globalˆb                        =          I(∑                             2 )
                                           m=1 w m       f m(Xb)≥
   6:                                                 Compute     Ac  c globalb                                              on  (Xb  ,     yb)
   7:                                                //    Step    2:    Tentative    local    incremental    update
   8:                                                 for    each    base    learner      M m   ∈E g      do
   9:                                                                                  θtemppartial_fit(M m  ,    Xb  ,     yb)
                                    m               ←
10:                                                end    for
11:                                                   Compute    updated    ensemble    predictions:
                                       M                                                     1
        y   localˆb                   =          I(∑       m              (Xb)≥2 )
                                     m=1 w m       f   temp
12:                                                  Compute  Ac  c localb
13:                                               //    Step    3:    Accuracy-Gated    Acceptance    Rule
14:                                                if       Ac  c localb                  ≥Ac  c globalb                      −δthen
15:                                                                      Accept    update
16:                                                                       Replace  M m   ←θtemp
                                                                         m                              for     all     m
17:                                                                      Transmit    updated    parameters    and    metrics    to    server
18:                                                                      Receive    updated    global    accuracy  Ac  c g
19:                                               else
20:                                                                      Reject    batch    update
21:                                                                        Discard     temporary     parameters
22:                                                end     if
23:               end     for

            To       operationalize       the       performance-weighted       aggregation       mechanism       described       above,       the       complete
server-side         procedure         is         summarized         in         Algorithm         2.         The         server         performs         robust         global         initialization
using     the     similarity-balanced     dataset,     followed     by     selective     aggregation     of     client     updates     based     on     accuracy
thresholds.    Only    updates    that    satisfy    the    global    acceptance    criterion    contribute    to    parameter    refinement    and
ensemble    weight    adjustment,    thereby     preventing     propagation    of     unreliable     gradients    into    the    global    model.

Algorithm    2:    Server-side     performance-weighted     federated     aggregation    with    accuracy-based    rejection
Require:    Balanced    initialization    dataset     D init ,     evaluation     dataset     D eval  ,     tolerance    γ
Ensure:     Up date d      g lob a l      ens emble        E g
   1:            Phase    I:    Robust    Global    Initialization
   2:               Train    base    learners  {M m}Mm=1    on     D init      using    incremental    partial_fit
   3:                Evaluate    ensemble    on     validation    subset    of    D eval
                                                                                                                                                                                                                                                         (Continued)
```


### PDF page 18

[View original page, figures and tables](assets/page-018.png)

```text
18                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                Comput   Model   Eng   Sci.    2026;147(3):48


Algorithm    2    (continued)
  4:               Compute    initial    global    accuracy      Ac  c g
  5:               Initialize    performance     weights {w m}Mm=1
  6:                Distribute  (E g  ,    Ac  c g)     to     clients
  7:               Phase    II:    Accuracy-Based    Federated    Aggregation
  8:                Upon    receiving     client    update  (Ec  ,    Ac  c c)
  9:               if       Ac  c c   <     γ⋅Ac  c g      then
10:                                                 Reject     update
11:                                                Return    currentAc  c g
12:               else
13:                                              for    each    base    learner      M m      do
14:                                                                                     Update     model     parameters:
                           θm+θ(c )
           θm   ←                2   m
15:                                                                                 Update    ensemble    weight:
           w m   ←w m   +       Ac c c2
16:                                              end     for
17:                                                 Ac  c g   ←max(Ac  c g  ,    Ac  c c)
18:                                                 Store     updated     global     ensemble
19:                                                  Return     updated  Ac  c g
20:               end     if

4        Results    and    Discussion
           In      this      section,      we      present      and      analyze      the      experimental      findings      of      the      proposed      resilient      federated
intrusion        detection        framework.        The        objective        is        to        examine        how        the        system        behaves        under        streaming,
non-IID,     and     adversarial     conditions     that     reflect     realistic     IoT     deployments.     We     evaluate     client-wise     stability,
batch-level    performance,    and    robustness    against    label-flipping    attacks.    In    addition,    ablation    experiments    are
conducted       to       understand       the       contribution       of       structured       global       initialization.       Rather       than       only       reporting
high-level    accuracy,    we    focus    on    convergence    behavior,    minority-class    sensitivity,    and    resistance    to    unstable
updates.      The      discussion      aims      to      connect      observed      empirical      trends      with      the      design      choices      introduced      in
the     proposed     methodology.

4.1        Experimental    Setup    and    Reproducibility
           All    experiments    were    implemented    in    Python    using    standard    scientific    and    machine    learning    libraries,
including        NumPy,        Pandas,        Scikit-learn,        and        Flask        for        client-server        communication.        The        evaluation        was
conducted      on      a      workstation      equipped      with      a      multi-core      CPU      and      sufficient      main      memory      for      streaming
batch    execution.
           The   CICIoT2023   dataset   was   preprocessed   using   label   encoding,   missing-value   handling,   and   min–max
normalization.   The   processed   data   were   partitioned   into   three   client   datasets   to   simulate   distributed   non-IID
federated    learning    conditions.
           Each   client   received   streaming   batches   sequentially.   For   every   batch,   local   evaluation   was   first   performed
using     the     current     global     model.     Updates     satisfying     the     acceptance     criterion     were     used     for     incremental     local
training    and    then    transmitted    to    the    server    for    weighted    aggregation.    Final    reported    metrics    were    computed
by     averaging    client-wise     results     over     the     full     streaming     process.
```


### PDF page 19

[View original page, figures and tables](assets/page-019.png)

```text
Comput   Model   Eng   Sci.    2026;147(3):48                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              19


         To        reduce        numerical        instability        and        experimental        bias,        normalized        features        were        used        throughout
training,   identical   preprocessing    was    applied    across    all    clients,   deterministic   data    partitions    were    maintained
during         evaluation,         and         multiple         complementary         metrics         were         reported,         including         Accuracy,         Precision,
Sensitivity,F1-score,MCC,Youden’sJ,andFMI.

4.2        Computational    Complexity    and    Runtime    Considerations
         The        proposed        framework        introduces        an        additional        preprocessing        stage        during        global        initialization
through      similarity-guided      balancing.      Let       N1   denotethenumberofdominant-classsamples.Thepairwise
similarity     computation     is     defined     in    Eqs.    (4)     and    (5)    require        O(N  21 )     operations     in     the     worst     case     due     to     all-
pairs   distance   evaluation   within   the   dominant   class.   However,    this   computation   is   executed   only   once   during
server-side     initialization    and    is    not    repeated     during     subsequent    federated     communication    rounds.
         Compared        with        conventional        federated        learning        approaches        that        directly        initialize        from        randomly
sampled      or      locally      available      data,      the      proposed      method      therefore      incurs      additional      initialization      cost      but
does     not     increase     recurring     online     communication     overhead.     During     federated     operation,     clients     continue
to    perform     lightweight    incremental    partial_fit    updates    on    streaming    mini-batches    and    transmit    only    model
parameters,    preserving     communication    behavior    comparable     to    standard    incremental    FL    settings.
         The      additional      initialization      overhead      is      compensated      by      improved      early-round      convergence      stability
and        reduced        propagation        of        unstable        updates        under        attack-dominant        traffic        distributions.        Furthermore,
for        large-scale        IoT        deployments,        the        preprocessing        stage        can        be        accelerated        using        approximate        nearest-
neighbor        search,        clustering-based         prototype         selection,         locality-sensitive         hashing,         or         parallel         block-wise
similarity     computation.

4.3        Client-Wise    Federated    Performance    Analysis
         This    subsection    analyzes    the    client-wise    behavior    of    the    proposed    streaming    federated    intrusion    detec-
tion    framework    in    relation    to    its    underlying    design    principles,    namely    similarity-guided    global    initialization,
incremental        ensemble        learning,        and        accuracy-gated        update        acceptance.        Rather        than        focusing        solely        on
aggregate         performance,          the          analysis         examines         batch-wise         dynamics         across          individual         clients         to         assess
stability,     robustness,     and     consistency     under     non-IID     streaming     conditions.
         Fig.    7     presents      the     federated     accuracy     progression      for     three      clients     over      successive     streaming     batches.
Across     all     clients,     accuracy     remains     tightly     bound     within     a     narrow     high-performance     band,     predominantly
between    0.97    and    0.99.    Importantly,    no    client   exhibits    sustained   accuracy   degradation    as    training   progresses.
This         behavior         is         non-trivial         in         streaming         federated         environments,         where         early         instability         and         concept
drift        often        amplify        local        errors.        The        observed        stability        can        be        attributed        to        the        similarity-guided        global
initialization     strategy,     which     produces     a     well-conditioned     starting     model     by     preserving     structurally     diverse
benign       samples       while       eliminating       majority-class       redundancy.       As       a       result,       early       federated       updates       are       not
dominated      by      biased      decision      boundaries,      allowing      subsequent      incremental      updates      to      refine      rather      than
correct     the     global     model.
         Short-lived   accuracy   fluctuations   are   visible   at   isolated   batches   for   individual   clients.   These   variations   are
expected   in   streaming   IoT   settings   due   to   localized   traffic   bursts,   transient   attack   patterns,   and   client-specific
distribution     shifts.     Crucially,     such     fluctuations     do     not     accumulate     across     batches,     indicating     that     unreliable
local     updates     are     effectively     prevented     from     influencing     the     global     ensemble.     This     behavior     directly     reflects
the    impact    of    the    accuracy-gated    update    acceptance    mechanism,    which    selectively     filters    batch    updates    that
would      otherwise      degrade      global      performance.      Consequently,      the      federation      exhibits      resilience      to      noisy      or
inconsistent    local    batches    without    suppressing    benign    adaptation.
```


### PDF page 20

[View original page, figures and tables](assets/page-020.png)

```text
20                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                Comput   Model   Eng   Sci.    2026;147(3):48



















                                           Figure    7:        Federated    accuracy    progression    per    client    across    streaming    batches.

           Fig.    8    complements    the    accuracy    analysis    by    reporting    the    Fowlkes–Mallows    Index    (FMI)    progression.
Unlike         accuracy,         FMI         jointly         captures         precision–recall         agreement         for         the         positive         (attack)         class         and         is
therefore      more      sensitive      to      class      imbalance      effects      common      in      IoT      intrusion      detection.      Across      all      clients,
FMI    remains    consistently    high    and    closely    tracks    the    accuracy    curves,    largely    exceeding    0.97    throughout    the
streaming     process.     The     absence     of     divergence     between     accuracy     and     FMI     trends     indicates     that     high     overall
accuracy       is       not       achieved       by       biasing       predictions       toward       the       dominant       class.       Instead,       the       model       preserves
reliable     attack-class    discrimination     across     clients     and     batches.



















                   Figure    8:         Federated    Fowlkes–Mallows    Index    (FMI)    progression    per    client    across    streaming    batches.

           The          consistency          between          accuracy          and          FMI          trends          indicates          that          the          ensemble          maintains          stable
minority-class    discrimination    throughout    streaming    adaptation.
           Ta  b  l  e        2     summarizes     the     aggregate     federated     performance     across     all     participating     clients.     The     achieved
accuracy         of         0.99         and         precision         of         1.00         indicate         a         strong         overall         detection         capability         under         distributed
operation       without       centralized       access       to       raw       data.       This       aggregate       evaluation       complements       the       client-wise
analysis    by    providing    a    global    view    of    the    final    federated    model.    However,    in    imbalanced    intrusion    detection
settings,     accuracy     alone     can     overstate     effectiveness     because     the     dominant     class     contributes     more     heavily     to
the     final     score.
```


### PDF page 21

[View original page, figures and tables](assets/page-021.png)

```text
Comput   Model   Eng   Sci.    2026;147(3):48                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           21


                                             Ta  b  l  e       2  :        Average    federated    performance    metrics    aggregated    across    all    clients.

Evaluation   Stage                                  Accuracy                                  Precision                                  Sensitivity                                  F1-Score                                      MCC                                      Markedness                                  YoudenJ                                          FMI
  Clients    Average                                                            0.99                                                                           1.00                                                                       0.8636                                                           0.7925                                           0.7870                                                         0.9881                                                                  0.8278                                           0.9898


           Although        the        overall        accuracy        is        high,        performance        should        be        interpreted        together        with        minority-
sensitive     metrics     such     as     Sensitivity,     F1-score,     MCC,     and     FMI.     These     measures     are     particularly     important     in
imbalanced    settings,    where    accuracy    alone    may     mask    bias    toward    the    dominant    attack    class.
           The      sensitivity      of      0.8636      and      F1-score      of      0.7925      indicate      that      minority-class      detection      remains      more
challenging    under    attack-dominant    and    non-IID    streaming    conditions,    where    class    skew    and    heterogeneous
client    distributions    can    affect    recall    and    precision    for    underrepresented    patterns.
           At      the      same      time,      the      MCC,      Markedness,      Youden’s      J,      and      FMI      values      remain      strong,      indicating      that
the        model        preserves        meaningful        discriminative        performance        and        does        not        rely        solely        on        majority-class
predictions.      Together,      the      client-level      trends      and      aggregate      metrics      indicate      that      the      proposed      framework
achieves      both      stable      local      adaptation      and      strong      global      federated      performance       through      similarity-guided
initialization,    incremental    ensemble    learning,    and    accuracy-aware    federation.

4.4        Robustness    against    Label-Flipping    Poisoning    Attacks
           This       section       evaluates       the       behavior       of        the       proposed        streaming       federated        learning       framework        under
complete       label-flipping       poisoning,       where       all       client-side       labels       are       inverted       prior       to       local       processing.       The
analysis      is      restricted      to      client-level      Accuracy,      as      shown      in     Fig.    9,      and      focuses      on      update      rejection      behavior
induced    by     the    accuracy-gated    mechanism.



















Figure      9:         Client-level      batch-wise      accuracy      under      complete      label-flipping      poisoning.      Across      all      clients      and      batches,
accuracy    remains    persistently    low,    fluctuating    approximately    between    0.01    and    0.036,    with    no    sustained    upward    trend.
All    batches    fall    below    the    acceptance    criterion,    resulting    in    systematic    rejection    of    local    updates.

           Fig.    9        shows        the        batch-wise        accuracy        trajectories        for        three        clients        under        complete        label        inversion.
For        all        clients,        accuracy        remains        consistently        low        throughout        the        streaming        process,        fluctuating        within
a        narrow        range        close        to        random-guess        performance        (approximately        0.01–0.036).        No        client        exhibits        sus-
tained      improvement      or      stabilization      across      batches,      and      no      batch      reaches      accuracy      levels      associated      with
benign    operation.
           As       a       direct       consequence       of       these       low       accuracy       values,       all       local       batches       fail       to       satisfy       the       accuracy-
gated     update     acceptance     criterion     and     are     rejected     prior     to     server     aggregation.     This     behavior     demonstrates
```


### PDF page 22

[View original page, figures and tables](assets/page-022.png)

```text
22                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                Comput   Model   Eng   Sci.    2026;147(3):48


deterministic    suppression     of     learning    under     maximal    label    corruption.     Since    no    client    updates    are    accepted
during    this    experiment,    the    results    do    not    permit    analysis    of    convergence,    recovery,    or    adaptation    dynamics
under     adversarial     influence.
              These       findings       are       limited       to       an       extreme       boundary-condition       scenario       in       which       all       client       labels       are
flipped.        Accordingly,        the        results        should        be        interpreted        strictly        as        empirical        evidence        of        fail-safe        update
rejection        under        complete        label-flipping        poisoning,        rather        than        as        robustness        to        partial,        probabilistic,        or
adaptive    poisoning    strategies.

4.5        Adversarial    Batch    Rejection    under    FGSM    Perturbation
              To        extend        the        robustness        evaluation        beyond         complete         label-flipping        attacks,        an        additional        experi-
ment       was       conducted       using       adversarially       perturbed       client       datasets       generated       with       the       Fast       Gradient       Sign
Method      (FGSM).      Three      independent      adversarial      datasets      were      created      in      separate      runs      using      randomized
seeds        and        assigned        to        three        federated        clients        for        streaming        evaluation        under        the        standard        training        and
communication    protocol.
              Adversarial       samples       were       generated       using       a       feed-forward       neural       network       surrogate       model       with       two
hidden      layers      of      128      neurons      each      and      ReLU      activation.      The      surrogate      model      was      trained      for      five      epochs
on     the     initialization     dataset.     FGSM     perturbations     were     then     applied     in     the     normalized     feature     space     using
randomly     selected     perturbation     magnitudes          ϵ  ∈[0.05,   0.25]     for     each     run.     After     perturbation,     the     generated
samples       were       mapped       back       to       the       original       feature       scale       while       preserving       their       original       class       labels.       Each
adversarial    dataset    contained    200,000    samples.
              Each      client      processed      200      streaming      batches,      resulting      in      a      total      of      600      batch-update      attempts      across
the     federation.     For     every      batch,     the     client     first     evaluated     the     current     global     ensemble      and     then     applied      the
proposed    accuracy-gating    acceptance    rule    before    any    local    update    could    be    transmitted    to    the    server.
              The        outcome        was        consistent        across        all        three        clients.        In        every        case,        the        batch-level        accuracy        of        the
adversarial    data    remained    below    the    required    acceptance    threshold,    and    all    attempted    updates    were    rejected
locally.    Consequently,    no    adversarial    update    was    forwarded     for    server-side    aggregation.
              As    shown    in    Ta  b  l  e        3,    all    FGSM-based    adversarial    batch    updates    were    rejected    across    the    three    federated
clients.       These       results       indicate       that       strongly       degraded       adversarial       inputs       can       be       effectively       filtered       before
entering          the          federated          aggregation          stage.          Although          FGSM          perturbation          does          not          cover          all          poisoning
scenarios     or     adaptive     adversarial     strategies,     the     experiment     provides     additional     evidence     that     the     proposed
gating    mechanism    can    block     low-quality    or     manipulated    client    updates    under    adversarial    conditions.

                                           Ta  b  l  e       3  :        FGSM-based    adversarial    batch    rejection    results    across    three    federated    clients.

  Client                                                                                                                                              Total    Batches                                                                                                                                        Accepted    Updates                                                                                                                                        Rejected    Updates
Client    1                                                                                                                                                                                       200                                                                                                                                                                                                                                                                 0                                                                                                                                                                                                                                                                                   200
Client    2                                                                                                                                                                                      200                                                                                                                                                                                                                                                                 0                                                                                                                                                                                                                                                                                   200
Client    3                                                                                                                                                                                      200                                                                                                                                                                                                                                                                 0                                                                                                                                                                                                                                                                                   200
    Total                                                                                                                                                                                                  600                                                                                                                                                                                                                                                                 0                                                                                                                                                                                                                                                                                   600


4.6        Ablation    Study:    Effect    of    Removing    Global    Initialization
              To   isolate   the   contribution   of   structured   global   initialization,   we   disable   the   similarity-guided   balancing
phase        and        skip        the        initial        incremental        training        over        Dinit  .        The        federated        process,        therefore,        begins        with
```


### PDF page 23

[View original page, figures and tables](assets/page-023.png)

```text
Comput   Model   Eng   Sci.    2026;147(3):48                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  23


randomly    initialized    BNB,    PA,    and    SGD    classifiers.    The    ensemble    aggregation,    client-side    0.95    accuracy    gat-
ing,     and     server-side     0.90     acceptance     threshold     remain     unchanged.     No     other     hyperparameters     are     modified.
          Cold-start     behavior     under     this     ablated     configuration     is     illustrated     in    Fig.    10.     The     degradation     is     imme-
diate.     Sensitivity     drops     to     0.6582,     while     overall     accuracy     settles     at     0.8159.     At     first     glance,     this     accuracy     may
appear    moderate.    However,    precision    increases    to    0.9616,    indicating    that    the    model    is    strongly    biased    toward
predicting    benign    traffic    during    early    batches.
















                                        Figure    10:      Cold-start    performance    without    structured    global    initialization.

          The         imbalance         propagates         across         other         performance         measures.         The         F1         score         decreases         to         0.7815,
reflecting     the     recall     loss.     The     Matthews     Correlation     Coefficient     (MCC)     falls     to     0.6659,     indicating     weakened
agreement     between     predictions     and     ground     truth.     Similarly,     the     Fowlkes–Mallows     Index     (FMI)     reduces     to
0.7146.    Markedness    (0.7017)    and    Youden’sJ      statistic     (0.6319)     further     confirm     that     the     decision     boundary     is
poorly     conditioned    at    initialization.
          Across   repeated   runs,   random   initialization   consistently   produced   unstable   early   optimization   behavior
and    weaker    minority-class    sensitivity    during    initial    communication    rounds.
          In     contrast,     the     initialized     configuration     discussed     earlier     stabilizes     near     the     0.97–0.99     accuracy     range
while       maintaining       substantially       higher       minority       recall.       The       divergence       between       the       two       settings       is       most
visible   during   the   first   communication   rounds.   Later   batches   show   partial   recovery   in   the   ablated   case,   but   the
early     vulnerability     window     remains     extended.     In     streaming     IoT     deployments,     that     early     phase     corresponds
to    live     traffic    conditions     and    therefore     carries     operational    significance.
          We        do        not        claim        that        structured        initialization        yields        theoretical        optimality.        The        experiment        simply
demonstrates     that     removing     principled     global     conditioning     degrades     early     stability     and     minority     detection
in    practice.    For    streaming    federated    intrusion    detection,    this    degradation    is    non-trivial.

4.7         Sensitivity    Analysis     of     Accuracy-Gating    Tolerance
          To      evaluate      the      effect      of      the      client-side      acceptance      tolerance,      additional      experiments      were      conducted
on       three       federated       clients       using       multiple       values       of       δ.       The       acceptance       rule       rejects       a       local       update       when       its
batch     accuracy     falls     below  (1−δ)     times     the     current     server     accuracy.     Four     operating     points     were     examined:
δ={0.01,   0.05,   0.10,   0.15},    corresponding    to    acceptance    thresholds    of    99%,    95%,    90%,    and    85%,    respectively.
          Ta  b  l  e        4      summarizes     the     results     in     terms     of     average     accepted-update     accuracy     and     the     total     number     of
accepted      packets/connections      (accepted      batch      updates).      A      stricter      threshold      yields      higher      average      update
quality       but       accepts       fewer       updates.       In       contrast,       relaxed       thresholds       improve       adaptation       by       accepting       more
updates,   with   a   small   reduction   in   average   accuracy.   The   95%   threshold   provides   a   balanced   trade-off   between
robustness     and     update     acceptance.
```


### PDF page 24

[View original page, figures and tables](assets/page-024.png)

```text
24                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                Comput   Model   Eng   Sci.    2026;147(3):48


                    Ta  b  l  e       4  :         Sensitivity    analysis    of    client-side    accuracy-gating    tolerance    under    different    acceptance    thresholds.

Acceptance    Threshold                                                                                                                                                                             Average    Accuracy                                                                                                                                                                             Accepted    Batch    Updates
                 99%    (δ=     0.01)                                                                                                                                                                                                                                                             0.9838                                                                                                                                                                                                                                                                                                                          88
                 95%     (δ=     0.05)                                                                                                                                                                                                                                                               0.9811                                                                                                                                                                                                                                                                                                                          137
                 90%    (δ=     0.10)                                                                                                                                                                                                                                                                          0.9796                                                                                                                                                                                                                                                                                                                                      210
                  85%     (δ=     0.15)                                                                                                                                                                                                                                                              0.9794                                                                                                                                                                                                                                                                                                                     238


4.8        Comparison    with    State-of-the-Art
                   Ta  b  l  e        5  summarizes   quantitative   performance   and   deployment   characteristics   of   recent   intrusion   detec-
tion   studies   evaluated   on   CICIoT2023   and   related   settings.   While   several   centralized   approaches   ([28–30,33])
report       very       high       accuracy       values,       many       are       limited       to       offline       evaluation.       Federated       learning       is       explored
in     [26],     but     without     poisoning     resilience     or     streaming     adaptation.     Incremental     approaches     ([31,32])     remain
centrally    coordinated.    As    observed,    high    accuracy    alone    does    not    imply    robustness    under    attack-dominated
imbalance     or     distributed     updates.     The     proposed     framework     differs     primarily     in     its     integration     of     streaming
federated        learning        with        structured        initialization        and        selective        update        acceptance        under        imbalanced        IoT
traffic    conditions.

                                                                                    Ta  b  l  e       5  :        Quantitative    comparison    with    state-of-the-art    on    CICIoT2023.

                                                                                                                                                                                                                                                                                                                                                                                              Real-World
                           Ref                                                                               Learning   Type                      Accurac y                          Precision                              Recall                                         F1                                                                                SpecialMechanism               Deployment
                                                                                                                                                                                                                                                                                                                                                                                        Consideration

        Abid    et    al.    [25]                                                   Centralized                                           95.24%                                            95.22%                                  86.39%                   95.09%                                                  GWO    andCNN-LGBM                                                                       Offline    only


       Torreetal.[    26]                                                        Federated                                                    97.31%                                            95.59%                                   92.43%                    92.69%                                                   DP      +    FHE                                                            10%    overhead;    nopoisoning    defense

       Okey    et    al.    [27]                                                  Centralized                                                     98%                                                                High                                                     High                                     High                           Model    compression                      Two-stage    training
     Wahabetal.[    28]                                            Centralized                                          99.20%                                                      94%                                                           93%                                           93%                                                SMOTE                                                  3Msubsetonly
         Mallikarjun    &
                Patro    [29]                                                                     Centralized                                           99.73%                                           99.73%                                   99.73%                    99.73%                           SVWS    balancing                                                          Binary    only
                  Wakili    &                                                     Centralized                                                                                                                                                                                                                                                                                           CPU-only    edge
            Bakkali   [30]                                                               Hybrid                                                          99.94%                                             95.53%                                  95.87%                    95.64%                                    Anomaly-firstcascade                                                    deployable

       Wa  n  g       e  t       a  l  .       [31]                                                Incremental(Centralized)                                    96.43%                                           96.59%                                  96.43%                   96.45%                      Weight    Alignment                                             High    runtime(789s)


     Mahdi    et    al.    [32]                                    Incremental      +Blockchain                                            99.89%                                           99.86%                                  99.92%                    99.89%                           Secure    retraining                                 Central    retrainingonly

              Doménech                                                                                                                                                                                                                                                                                                                                                            Shows    dataset    shift
                  et    al.    [33]                                                                        Centralized                                          99.85%                                            96.91%                                    97.12%                       97.00%                                                  SMOTE      +optimized    splits                         issue

     Saxena    et    al.    [34]                                            Centralized(GNN)                                                         90.69%                                                      0.90(weighted)                                            –                                                    0.90                                          Graph    modeling                                                           We  a  k       m  i  n  o r  i t  yclass    precision

                                                                                                                                                                                                                                                                                                         Similarity-guided                                                           Cold-start-aware
                 Proposed                                                                             Federated                                                           99%                                                              100%                                        86.36%                    79.25%data    balancing                                                   initialization;
                                                                                                                                                                                                                                                                                                                          strategy                                                               streaming
                                                                                                                                                                                                                                                                                                                                                                                   federated    learning
```


### PDF page 25

[View original page, figures and tables](assets/page-025.png)

```text
Comput   Model   Eng   Sci.    2026;147(3):48                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                25


4.9        Communication    Cost,    Computational    Efficiency,    and    Scalability
          Beyond        predictive        performance,        practical        federated        IoT        deployment        requires        attention        to        commu-
nication        cost        and        computational        efficiency.        The        proposed        framework        uses        incremental        linear        classifiers,
which    update    model    parameters    batch-wise    without    repeated    full    retraining,    reducing    client-side    processing
overhead.     In     addition,     mRMR-based     feature     selection     reduces     the     original     46-dimensional     feature     space     to
31     features,    lowering     both    training    cost    and    data    handling    complexity.
          Communication       overhead       is       also       reduced       through       the       proposed       accuracy-gating       mechanism.       Only
clients        whose        local        batch        performance        satisfies        the        acceptance        criterion        transmit        updated        models        to        the
server.        This        avoids        unnecessary        communication        from        low-quality        or        corrupted        updates        and        can        reduce
uplink     traffic     under     unstable     client     conditions.
          The      similarity-guided      balancing      stage      is      executed      once      during      server-side      initialization      and      therefore
does       not       add       recurring       communication       cost       during       federation.       Its       quadratic       worst-case       complexity       may
become   expensive   for   very   large   datasets,   but   this   step   can   be   accelerated   using   approximate   nearest-neighbor
search,    block-wise    similarity    computation,    parallel    processing,    or    sampled    initialization    subsets.
          For      larger      federated      deployments,      the      framework      can      be      extended      through      client      subsampling,      asyn-
chronous        participation,        or        hierarchical        aggregation        across        edge        gateways.        These        strategies        can        improve
scalability    while    preserving     the    proposed     update    filtering     mechanism.

4.10        Threats    to    Validity
          As    the    present    study    is    based    on    simulation    using    the    CICIoT2023    dataset,    the    reported    findings    should
be    interpreted    with    appropriate    validity    considerations.
          Internal     Validity:     Internal     validity     may     be     affected     by     preprocessing     choices,     client     data     partitioning,
hyperparameter      settings,      and      assumptions      used      in      the      simulated      federated      environment.      To      reduce      these
effects,        consistent        preprocessing        was        applied        across        all        clients,        fixed        evaluation        settings        were        used,        and
multiple    complementary    metrics    were    reported    instead    of    relying    on    a    single    performance    measure.
          External   Validity:   External   validity   concerns   the   generalization   of   the   results   beyond   the   current   dataset
and     simulation     setting.     Real     IoT     deployments     may     exhibit     different     traffic     distributions,     larger     numbers     of
clients,       changing       network       conditions,       device       constraints,       and       more       adaptive       attack       behaviors       than       those
modeled     here.     Therefore,     performance     may     vary     under     other     datasets    or     operational     environments.
          Future   work   will   include   validation   on   additional   datasets,   larger-scale   federated   settings,   and   real-world
deployment     scenarios.

4.11         Effect     of     Initialization     on     Early     Federated     Stability
          To    further    examine    the    effect    of    early    federated    initialization,    an    additional    experiment    was    conducted
using        three        alternative        starting        conditions        for        the        global        model:        random        balanced        initialization,        attack-
dominant       skewed       initialization,       and       the       proposed       similarity-guided       initialization.       In       all       cases,       the       same
client     datasets,     streaming     protocol,     and     aggregation     settings     were     maintained     so     that     only     the     initialization
strategy     varied.
          The        random       setting       used       an       equal       number       of        benign       and       malicious       samples        selected        uniformly       at
random.       The       skewed       setting       used       an       attack-dominant       initialization       set       with       a       90:10       malicious-to-benign
ratio.    The    proposed     setting    used    the    similarity-guided    balanced    initialization    described    in    Section    3.2.
          Ta  b  l  e        6         reports         the         final         aggregate         performance.         The         proposed         initialization         achieved         the         highest
Accuracy   (0.979596)    and   FMI   (0.979392),    followed    by    the   skewed    and   random    settings.   These   results    suggest
```


### PDF page 26

[View original page, figures and tables](assets/page-026.png)

```text
26                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                Comput   Model   Eng   Sci.    2026;147(3):48


that      initialization      quality      influences      downstream      federated      learning      performance,      and      that      a      balanced      yet
structurally    diverse     starting    model     provides     improved     convergence     reliability.

                                                            Ta  b  l  e       6  :         Impact    of    initialization    strategy    on    federated    performance.

              Experiment                                                                                                                                                                                                                                                                                                                                            Accuracy                                                                                                                                                                                                                                                                                                                FMI
 Random    Initialization                                                                                                                                                                                                                                                                                                   0.975008                                                                                                                                                                                                                                                                                                0.975414
  Skewed    Initialization                                                                                                                                                                                                                                                                                                        0.978662                                                                                                                                                                                                                                                                                                 0.978391
Proposed     Initialization                                                                                                                                                                                                                                                                                                0.979596                                                                                                                                                                                                                                                                                                0.979392


5        Conclusions
             This        work        investigated        federated        intrusion        detection        under        sustained        IoT        attack        conditions,        where
malicious       traffic       may       dominate       the       data       stream       and       create       severe       imbalance       during       deployment.       Unlike
conventional        settings        in        which        benign        traffic        overwhelms        rare        attacks,        ongoing        attack        scenarios        reverse
this     distribution     and     introduce     a     different     form     of     instability.     When     attack-heav y     gradients     dominate     early
federated       rounds,       the       global       model       can       overfit       malicious       patterns,       weakening       discrimination       of       residual
benign    traffic    and    increasing    false    alarms    or     misclassification    after    attack    intensity    subsides.
             To        address        this        challenge,        we        introduced        a        similarity-guided        balancing        mechanism        that        preserves
structurallydiversesamplesfromthedominantclass                        while        constructing        a        stable        and        class-conditioned
initialization       dataset.       The       balancing       stage       is       performed       once       during       server-side       initialization       and       can       be
accelerated    through    parallel,    block-wise,    or    approximate    similarity    computation    in    large-scale    deployments.
The        framework        further        integrates        mRMR-based        feature        selection,        reducing        the        original        46-dimensional
CICIoT2023    feature    space    to    31    informative    features    through    an    80%    retention    criterion    based    on    combined
relevance-redundancy      scores.      This      compact      representation      improves      efficiency      while      preserving      discrimi-
native     traffic     characteristics.     In     addition,     the     proposed     framework     employs     incremental     ensemble     learning
for        continuous        adaptation        and        an        accuracy-gated        update        mechanism        that        selectively        filters        unreliable        or
corrupted     client    updates.
             Experimental       evaluation       demonstrates       stable       convergence       across       clients,       strong       agreement       between
accuracy         and         minority-sensitive         metrics,         and         deterministic         rejection         of         updates         under         complete         label-
flipping    poisoning.    The    ablation    study    confirms    that    removing    structured    initialization    increases    early-stage
bias       and       extends       the       vulnerability       window.       An       additional       initialization       study       further       confirmed       that       the
proposed      similarity-guided      starting      model      yields      stronger      federated      performance      than      random      or      attack-
dominant      initialization      baselines.      These      results      indicate      that      robust      initialization,      selective      federation,      and
principled     feature     reduction     jointly     improve     detection     reliability     in     streaming     IoT     environments     operating
under    adversarial    and    imbalanced    conditions.
             Few    limitations    remain.    First,    although    the    similarity-based    redundancy    computation    is    an    offline    one-
time        operation,        its        quadratic        worst-case        complexity        may        still        require        approximation        for        extremely        large
IoT      telemetry      streams.      Second,      adversarial      evaluation      was      limited      to      complete      label-flipping      and      strongly
degraded     adversarial     batches;     more     subtle,     adaptive,     partial,     stealthy,     or     collusive     poisoning     strategies     were
not      examined.      Third,      the      use      of      lightweight      linear      incremental      classifiers      may      restrict      expressive      capacity
under        highly        nonlinear        traffic        dynamics        or        severe        cross-domain        distribution        shifts.        Fourth,        the        current
performance-weighted       aggregation      relies       primarily       on      local      accuracy      and      may      favor      clients      with      trivially
high-performing        local        data.        Fifth,        a        formal        convergence        guarantee        under        non-IID        streaming        data        with
```


### PDF page 27

[View original page, figures and tables](assets/page-027.png)

```text
Comput   Model   Eng   Sci.    2026;147(3):48                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      27


dynamic       client       acceptance       and       adversarial       behavior       was       not       derived       in       this       study       due       to       non-stationary
distributions,    incremental    updates,    and    time-varying    participation     sets.
         Future       work       will       address       these       limitations       by       developing       approximate       or       distributed       similarity       esti-
mation     techniques     for     scalable     initialization,     incorporating     adaptive     trust     or     reputation-aware     aggregation
mechanisms         to         counter         stealthy         adversaries,         exploring         lightweight         nonlinear         incremental         models         with
domain-adaptive      capabilities,      and      investigating      theoretical      convergence      under      selective      participation      with
robustness      bounds      against      poisoning      attacks.      These      extensions      aim      to      strengthen      robustness      in      prolonged
real-world   attack   scenarios   while   preserving   the   privacy,   communication,   and   streaming   constraints   inherent
to    federated    IoT    intrusion    detection.

Acknowledgement:       The    authors    extend    their    appreciation   to    Umm    Al-Qura    University,    Saudi    Arabia,    for    funding    this
research    work    through    grant    number:    26UQU4290235GSSR01.

Funding    Statement:       This    research    work    was    funded    by    Umm    Al-Qura    University,    Saudi    Arabia    under    grant    number:
26UQU4290235GSSR01.

Author       Contributions:          Arvind       Prasad       contributed       to       conceptualization,       methodology,       experimental       design,       data
curation,      formal      analysis,      software      implementation,      writing      of      the      original      draft,      and      manuscript      revision.      Ibrahim
Aljubayri    contributed   through    visualization,    expert    consultation,   and    professional   guidance.    Mohammad    Zubair    Khan
contributed   to   supervision,   validation,   visualization,   and   critical   manuscript   review   and   editing.   Abdulfattah   Noorwali
contributed    to    funding    acquisition,    investigation,    and    visualization.    All    authors    reviewed    the    results    and    approved    the
final    version    of    the    manuscript.

Availability     of     Data     and     Materials:        The     CICIoT2023     dataset     used     in     this     study     is     publicly     available     at  https://www.
unb.ca/cic/datasets/iotdataset-2023.html.

Ethics    Approval:        Not     applicable.

Conflicts    of    Interest:       The    authors    declare    no    conflicts    of    interest.

References
1.                           Al-Quayed    F.    AI-powered    anomaly    detection    and    cybersecurity    in    healthcare    IoT    with    fog-edge.    Comput    Model
         Eng    Sci.    2026;146(1):1–10.    doi:10.32604/cmes.2025.074799.
2.                        Abdulganiyu      OH,      Fadi      O,      Moukafih      Y,      Ait      Tchakoucht      T,      Saheed      YK,      Chukwuere      JE,      et      al.      Explainable      atten-
         tion        based        few        shot        LSTM        for        intrusion        detection        in        imbalanced        cyber        physical        system        networks.        Sci        Rep.
         2026;16(1):7217.    doi:10.1038/s41598-026-38668-4.
3.                         Hazman     C,     Guezzaz     A,     Benkirane     S,     Azrour     M.     A     smart     model     integrating     LSTM     and     XGBoost     for     improving
         IoT-enabled    smart    cities    security.    Clust    Comput.    2024;28(1):70.    doi:10.1007/s10586- 024- 04780- 1.
4.                        Singh    S,    Tyagi    V,    Malik    A,    Kumar    R,    Ankur,    Kumar    N.    Intelligent    energy-aware    routing    via    protozoa    behavior    in
         IoT-enabled    WSNs.    IEEE    Trans    Netw    Serv    Manage.    2026;23:1960–9.    doi:10.1109/TNSM.2025.3636202.
5.                         Prasad   A,   Chandra   S.   BotDefender:   a   collaborative   defense   framework   against   botnet   attacks   using   network   traffic
         analysis    and    machine    learning.    Arab    J    Sci    Eng.    2024;49(3):3313–29.    doi:10.1007/s13369- 023- 08016- z.
6.                        Khasawneh      M,      Azab      A,      Alrabaee      S,      Sakkal      H,      Bakhit      HH.      Convergence      of      IoT      and      cognitive      radio      networks:
         a      survey      of      applications,      techniques,      and      challenges.      IEEE      Access.      2023;11:71097–112.      doi:10.1109/ACCESS.2023.
         3294091.
7.                           Al-Bakhrani     AA,     Li     M,     Obaidat     MS,     Amran     GA.     MOALF-UAV-MEC:     adaptive     multiobjective     optimization     for
         UAV-assisted   mobile   edge   computing   in   dynamic   IoT   environments.   IEEE   Internet   Things   J.   2025;12(12):20736–56.
         doi:10.1109/JIOT.2025.3544624.
8.              KarmousN,JlassiW,AoueileyineMO,FilaliI,BouallegueR.AnewdatasetfornetworkfloodingattacksinSDN-
         based    IoT    environments.    Comput    Model    Eng    Sci.    2025;145(3):4363–93.    doi:10.32604/cmes.2025.074178.
```


### PDF page 28

[View original page, figures and tables](assets/page-028.png)

```text
28                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                Comput   Model   Eng   Sci.    2026;147(3):48


9.                         Joe      M,      Kim      M,      Kwon      M.      Contrastive      learning      based      network      attack      classifier      for      imbalanced      data.      J      Commun
         Netw.    2026;28(1):86–97.    doi:10.23919/JCN.2025.000082.
10.                 Kim      MG,      Kim      H.      Anomaly      detection      in      imbalanced      encrypted      traffic      with      few      packet      metadata-based      feature
         extraction.    Comput    Model    Eng    Sci.    2024;141(1):585–607.    doi:10.32604/cmes.2024.051221.
11.                    Saba   T,   Sadad   T,   Rehman   A,   Mehmood   Z,   Javaid   Q.   Intrusion   detection   system   through   advance   machine   learning
         for    the    Internet    of    Things    networks.    IT    Prof.    2021;23(2):58–64.    doi:10.1109/MITP.2020.2992710.
12.                  Li     C,     Li     J,     Liu     M,     Wang     H.     Entropy-driven     personalized     privacy     and     dynamic     federated     learning     inIoTSystems.
         Secur    Priv.    2026;9(1):e70180.    doi:10.1002/spy2.70180.
13.                  Patnaik         LM,         Wang         W.         AI         fairness–from         machine         learning         to         federated         learning.         Comput         Model         Eng         Sci.
         2024;139(2):1203–15.    doi:10.32604/cmes.2023.029451.
14.                 Khan    AY,    Latif    R,    Latif    S,    Tahir    S,    Batool    G,    Saba    T.    Malicious    insider    attack    detection    in    IoTs    using    data    analytics.
         IEEE    Access.    2020;8:11743–53.    doi:10.1109/ACCESS.2019.2959047.
15.                  Prasad    A,    Mohammad    Alenazy    W,    Ahmad    N,    Ali    G,    Abdallah    HA,    Ahmad    S.    Optimizing    IoT    intrusion    detection
         with     cosine     similarity     based     dataset     balancing     and     hybrid     deep     learning.     Sci     Rep.     2025;15(1):30939.     doi:10.1038/
         s41598-025-15631-3.
16.                 Sánchez       PMS,       Celdrán       AH,       Schenk       T,       Iten       ALB,       Bovet       G,       Pérez       GM,       et       al.       Studying       the       robustness       of       anti-
         adversarial      federated      learning      models      detecting      cyberattacks      in      IoT      spectrum      sensors.      IEEE      Trans      Dependable
         Secure    Comput.    2024;21(2):573–84.    doi:10.1109/TDSC.2022.3204535.
17.                     Lei    T.    Securing    Fog-enabled    IoT:    federated    learning    and    generative    adversarial    networks    for    intrusion    detection.
         Telecommun    Syst.    2025;88(1):11.    doi:10.1007/s11235-024-01237-z.
18.           PathakJ,MundraP,SejpalY,MahapatraT,RajputAS.Earlyrounddetectionprotocols:strategiesagainstuntargeted
         adversarial        attacks        in        federated        learning        network.        Comput        Netw.        2026;279:112098.        doi:10.1016/j.comnet.2026.
         112098.
19.                  Prasad    A,    Chandra    S,    Uddin    M,    Al-Shehari    T,    Alsadhan    NA,    Sajid    Ullah    S.    PermGuard:    a    scalable    framework    for
         Android    malware    detection    using    permission-to-exploitation    mapping.    IEEE    Access.    2025;13:507–28.    doi:10.1109/
         ACCESS.2024.3523629.
20.               Alshehri     MS,     Saidani     O,     Al     Malwi     W,     Asiri     F,     Latif     S,     Ahmad     Khattak     A,     et     al.     A     hybrid     Wasserstein     GAN     and
         autoencoder     model     for     robust     intrusion     detection     in     IoT.     Comput     Model     Eng     Sci.     2025;143(3):3899–920.     doi:10.
         32604/cmes.2025.064874.
21.                  Tyagi    V,    Singh    S,    Wu    H,    Gill    SS.    Load    balancing    in    SDN-enabled    WSNs    toward    6G    IoE:    partial    cluster    migration
         approach.    IEEE    Internet    Things    J.    2024;11(18):29557–68.    doi:10.1109/JIOT.2024.3402266.
22.               Malik     A,     Tyagi     V,     Singh     S,     Kumar     R,     Wu     H,     Gill     SS.     Optimizing     secure     data     transmission     in     6G-enabled     IoMT
         using    blockchain    integration.    IEEE    Trans    Consumer    Electron.    2025;71(2):4534–43.    doi:10.1109/TCE.2024.3510812.
23.               Grispos    G,    Studiawan    H,    Alrabaee    S.    Internet    of    Things    (IoT)    forensics    and    incident    response:    the    good,    the    bad,
         and    the    unaddressed.    Forensic    Sci    Int    Digit    Investig.    2024;48(3):301671.    doi:10.1016/j.fsidi.2023.301671.
24.               Prasad       A,       Chandra       S,       Alenazy       WM,       Ali       G,       Shah       S,       ElAffendi       M.       AndroMD:       an       Android       malware       detection
         framework    based    on    source    code    analysis    and    permission    scanning.    Results    Eng.    2025;28(1):107050.    doi:10.1016/j.
         rineng.2025.107050.
25.               Abid     T,     Ahmim     A,     Maazouzi     F,     Chefrour     D,     Ullah     I,     Ahmim     M,     et     al.     A     novel     IoT     threat     detection     using     GWO
         feature    selection   and   CNN-enhanced   LightGBM.    J    Cloud    Comput.   2025;14(1):72.    doi:10.1186/s13677-025- 00785-2.
26.               Torre       D,       Chennamaneni       A,       Jo       J,       Vyas       G,       Sabrsula       B.       Toward       enhancing       privacy       preservation       of       a       federated
         learning    CNN    intrusion    detection    system    in    IoT:    method    and    empirical    study.    ACM    Trans    Softw    Eng    Methodol.
         2025;34(2):1–48.    doi:10.1145/3695998.
27.                  Okey       OD,       Dadkhah       S,       Rodríguez       DZ,       Kleinschmidt       JH.       Explainable       resource-Aware       IoT       security       model       via
         knowledge   distillation   and   adaptive   loss   function   optimization.   Expert   Syst   Appl.   2026;302(7):130460.   doi:10.1016/
         j.eswa.2025.130460.
28.               Wahab      SA,      Sultana      S,      Tariq      N,      Mujahid      M,      Ali      Khan      J,      Mylonas      A.      A      multi-class      intrusion      detection      system
         for     DDoS     attacks     in     IoT     networks     using     deep     learning     and     transformers.     Sensors.     2025;25(15):4845.     doi:10.3390/
         s25154845.
```


### PDF page 29

[View original page, figures and tables](assets/page-029.png)

```text
Comput   Model   Eng   Sci.    2026;147(3):48                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            29


29.                Mallikarjun       A,       Patro       P.       Hybrid       data       balancing       with       MLP       probabilities-based       categorical       boosting       model       for
         robust      intrusion      detection      system      in      IoT      environment.      Syst      Soft      Comput.      2026;8(16):200443.      doi:10.1016/j.sasc.
         2026.200443.
30.               Wakili    A,    Bakkali    S.    ZeroDefense:    an    adaptive    hybrid    fusion-based    intrusion    detection    system    for    zero-day    threat
         detection    in    IoT    networks.    J    Electron    Sci    Technol.    2026;24(1):100345.    doi:10.1016/j.jnlest.2026.100345.
31.                   Wang      H,      Yang      Y,      Tan      P.      CTWA:      a      novel      incremental      deep      learning-based      intrusion      detection      method      for      the
         Internet    of    Things.    Artif    Intell    Rev.    2025;58(12):374.    doi:10.1007/s10462-025-11358-9.
32.                Mahdi      ZS,      Zaki      RM,      Alzubaidi      L.      A      secure      and      adaptive      framework      for      enhancing      intrusion      detection      in      IoT
         networks    using    incremental    learning    and    blockchain.    Secur    Priv.    2025;8(4):e70071.    doi:10.1002/spy2.70071.
33.                Doménech    J,    León    O,    Siddiqui    MS,    Pegueroles    J.    Evaluating    and    enhancing    intrusion    detection    systems    in    IoMT:
         the    importance    of    domain-specific    datasets.    Internet    Things.    2025;32(1):101631.    doi:10.1016/j.iot.2025.101631.
34.               Saxena    S,    Grover    J,    Singhal    S.    Exploring    graph    neural    networks    for    robust    network    intrusion    detection.    Procedia
         Comput    Sci.    2025;258(10):3630–9.    doi:10.1016/j.procs.2025.04.618.
35.     FarhanS,MubashirJ,HaqYU,MahmoodT,RehmanA.Enhancingnetworksecurity:anintrusiondetection
         system      using      residual      network-based      convolutional     neural      network.      Clust      Comput.      2025;28(4):251.      doi:10.1007/
         s10586-025-05156-9.
36.               Alrayes     FS,     Amin     SU,     Hakami     N.     An     adaptive     framework     for     intrusion     detection     in     IoT     security     using     MAML
         (model-agnostic    meta-learning).    Sensors.    2025;25(8):2487.    doi:10.3390/s25082487.
37.                   Prasad     A,     Chandra     S.     PhiUSIIL:     a     diverse     security     profile     empowered     phishing     URL     detection     framework     based
         on    similarity    index    and    incremental    learning.    Comput    Secur.    2024;136(4):103545.    doi:10.1016/j.cose.2023.103545.
38.               Neto        ECP,        Dadkhah       S,        Ferreira        R,        Zohourian       A,        Lu       R,        Ghorbani        AA.        CICIoT2023:       a        real-time       dataset       and
         benchmark    for    large-scale    attacks    in    IoT    environment.    Sensors.    2023;23(13):5941.    doi:10.3390/s23135941.
39.                Khalil   A,   Farman   H,   Nasralla   MM,   Jan   B,   Ahmad   J.   Artificial   Intelligence-based   intrusion   detection   system   for   V2V
         communication    in    vehicular    adhoc    networks.    Ain    Shams    Eng    J.    2024;15(4):102616.    doi:10.1016/j.asej.2023.102616.
40.              Prasad   A,   Yadav   V,   Solanki   C,   Goswami   H,   Jha   T,   Nagal   D.   StealthPhisher:   a   defensive   framework   against   phishing
         attack        using        hybrid        deep        learning        and        GenAI.        Expert        Syst        Appl.        2026;299(4):130205.        doi:10.1016/j.eswa.2025.
         130205.
41.     ZhaoZ,ZhengM,MaF,LiT.Anovelfederatedadaptivehybridsamplingframeworkforimbalanceddata
         classification.    Appl    Soft    Comput.    2026;193(8):114866.    doi:10.1016/j.asoc.2026.114866.
42.              Zhao    X,    Wu    Y,    Chaddad    A,    Daqqaq    T,    Kateb    R.    Federated    vision    transformer    with    adaptive    focal    loss    for    medical
         image    classification.    Knowl    Based    Syst.    2026;338(Suppl    3):115474.    doi:10.1016/j.knosys.2026.115474.
43.               Alnajar     O,     Barnawi     A.     A     novel     clustered     distributed     federated     learning     architecture     for     tactile     Internet     of     Things
         applications    in    6G    environment.    Comput    Model    Eng    Sci.    2025;143(3):3861–97.    doi:10.32604/cmes.2025.065833.
44.             Martinez-Lopez   F,   Santana   L,   Rahouti   M,   Chehri   A,   Al-Maliki   S,   Jeon   G.   Learning   in   multiple   spaces:   prototypical
         few-shot        learning        with        metric        fusion        for        next-generation        network        security.        IEEE        Trans        Netw        Serv        Manage.
         2026;23:3156–65.    doi:10.1109/TNSM.2026.3665647.
45.               Krouka   M,   Ben   Issaid   C,   Bennis   M.   Distributionally   robust   federated   learning   with   client   drift   minimization.   Trans
         Mach    Learn    Comm    Netw.    2026;4:438–56.    doi:10.1109/TMLCN.2026.3658026.
```
