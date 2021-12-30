Þ          Ì               |  ½   }     ;     É     \     i  S  n  	   Â     Ì  4  à  Ô     Ô   ê     ¿  !   È  J  ê     5	  º   H	  z   
     ~
  I     1  ]  º    t  J     ¿  {   T     Ð  
   c     n  3  s  	   §     ±    À  º   È  À        D  !   K    m     ~  ¡     c   0       D     ð   _    P   **Access APIs** of the components of FDI data objects are convenient and similar to those of standad Python libraries, making it easier for **scripting and data mining** directly 'on FDIs'. A reference REST API server designed to communicate with a data processing docker using the data model is in package  :doc:`pns <usage/pns>`. A reference REST API server to provide a web interface between a pool on the server and a data user in package  :doc:`http pool <usage/httppool>`. API Document API: All levels of FDI Products and their components (datasets or metadata) are portable (**serializable**) in human-friendly standard format (JSON implemented), allowing machine data processors on different platforms to parse, access internal components, or re-construct a product. Even a human with only a web browser can understand the data. Contents: FDI Python packages FDI helps data producers and processors to build connections into isolated heterogeneous datasets. to assemble, organize, and integrate data into self-describing, modular, hierarchical, persistent, referenceable ``Products``, whose component datasets keep their own characteristics and are easily accessible. FDI provides *Context* type of product so that references of other products can become components, enabling **encapsulation of rich, deep, sophisticated, and accessible contextual data**, yet remain light weight. FDI stoerage 'pools' (file, network, or memory based) are provided as references for 1) **queryable** data **storage** and, 2) for all persistent data to be referenced to with **URNs** (Universal Resource Names). Features Flexible Dataset Integrator (FDI) For data processors, an HTML **server** with **RESTful APIs** is implemented (named Processing Node Server, PNS) to interface data processing modules. PNS is especially suitable for **Docker containers** in pipelines mixing **legacy software** or software of incompatible environments to form an integral data processing pipeline. Indices and tables Most FDI Products and components implement **event sender and listener interfaces**, helping **scalable data-driven** processing pipelines and visualizers of live data to be constructed. Persistent data access, referencing, querying, and Universal Resource Names are defined in package :doc:`pal <usage/pal>`. The ``toString()`` method of major containers classes outputs nicely formated (often tabulated) text description of complex data to help inspection. The base data model is defined in package :doc:`dataset <usage/dataset>`. This package attempts to meet scientific observation and data processing requirements, and is inspired by data models of, and designs APIs as compatible as possible with, European Space Agency's Interactive Analysis package of Herschel Common Science System (written in Java, and in Jython for scripting). With FDI one can pack data of different format into **regular and modular** data ``Products``, together with annotation (description, types, units, defaults, and validity specifications) and meta data (data about data). One can make arrays or tables of Products using basic data structures such as sequences (e.g. Python ``list``), mappings (e.g. Python ``dict``), or custom-made classes. FDI accomodates nested and highly complex structures. Project-Id-Version: fdi 
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2021-12-30 09:03+0800
PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE
Last-Translator: FULL NAME <EMAIL@ADDRESS>
Language: zh_CN
Language-Team: zh_CN <LL@li.org>
Plural-Forms: nplurals=1; plural=0
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 2.9.1
 FDI æ°æ®å¯¹è±¡è½ä¾¿æ·å°è®¿é® APIï¼ä½¿ç¨æ¹å¼ç±»ä¼¼äºæ å Python åºç APIï¼ä¾¿äºç´æ¥å¨ FDI ä¸è¿è¡èæ¬ç¼ååæ°æ®ææã åè REST API æå¡å¨ï¼æ¨å¨ä½¿ç¨æ°æ®æ¨¡åä¸æ°æ®å¤ç docker éä¿¡ï¼ä½äºå :doc:`pns <usage/pns>` ä¸­ã åè REST API æå¡å¨ï¼ç¨äºå¨æå¡å¨ä¸çæ± åæ°æ®ç¨æ·ä¹é´æä¾ Web çé¢ï¼ä½äºå :doc:`http pool <usage/httppool>` ä¸­ã API ææ¡£ API: ææçº§å«ç FDI äº§ååå¶ç»æé¨åï¼æ°æ®éæåæ°æ®ï¼å¯ä½¿ç¨äººæ§åçæ åæ ¼å¼ï¼JSONï¼è¿è¡ç§»æ¤ï¼**å¯åºåå**ï¼ï¼åè®¸ä¸åå¹³å°ä¸çæºå¨æ°æ®å¤çå¨è§£æãè®¿é®åé¨ç»ä»¶æéæ°æå»ºäº§åãå³ä½¿æ¯åªæç½ç»æµè§å¨çäººç±»ä¹è½çè§£æ°æ®ã åå®¹ï¼ FDI Python å FDI å¸®å©æ°æ®çäº§èåå¤çèå¨å­¤ç«çå¼ææ°æ®éç´æ¥å»ºç«è¿æ¥ã å°è¿äºæ°æ®ç»è£ãç»ç»åéæå°èªæè¿°çãæ¨¡ååçãåå±çãæä¹çãå¯å¼ç¨çäº§åä¸­ï¼ä½¿åæ°æ®éä¿æèªå·±çç¹å¾å¹¶ä¸æäºè®¿é®ã FDI æä¾ *Context* ç±»åçäº§åï¼ä»¥ä¾¿å¶ä»äº§åçå¼ç¨å¯ä»¥æä¸ºç»ä»¶ï¼ä»èè½å¤å°è£ä¸°å¯ãæ·±å¥ãå¤æåå¯è®¿é®çä¸ä¸ææ°æ®ï¼åæ¶ä¿æè½»éçº§ã æä¾ FDI å­å¨âæ± âï¼åºäºæä»¶ãç½ç»æåå­ï¼ä½ä¸ºåèï¼ç¨äº 1ï¼å¯æ¥è¯¢æ°æ®å­å¨ï¼2ï¼æææä¹æ°æ®é½å¯ä»¥éè¿ URNï¼éç¨èµæºåç§°ï¼è¿è¡å¼ç¨ã åè½ çµæ´»çæ°æ®ééæå¨ (FDI) å¯¹äºæ°æ®å¤çå¨ï¼å®ç°äºå¸¦æ RESTful API ç HTML æå¡å¨ï¼ç§°ä¸ºå¤çèç¹æå¡å¨ï¼PNSï¼ä»¥è¿æ¥æ°æ®å¤çæ¨¡åã PNS ç¹å«éç¨äºç®¡éä¸­ç Docker å®¹å¨æ··åéçè½¯ä»¶æä¸å¼å®¹ç¯å¢çè½¯ä»¶ï¼ä»¥å½¢æå®æ´çæ°æ®å¤çç®¡éã ç´¢å¼åè¡¨æ ¼ å¤§å¤æ° FDI äº§ååç»ä»¶é½å®ç°äºäºä»¶åéå¨åä¾¦å¬å¨æ¥å£ï¼æå©äºæå»ºå¯æ©å±çæ°æ®é©±å¨å¤çç®¡éåå®ç°å®æ¶æ°æ®å¯è§åã æä¹æ°æ®è®¿é®ãå¼ç¨ãæ¥è¯¢åéç¨èµæºåç§°å¨å :doc:`pal <usage/pal>` ä¸­å®ä¹ã ä¸»è¦å®¹å¨ç±»ç ``toString()`` æ¹æ³è¾åºå¤ææ°æ®çæ ¼å¼åå¥½çææ¬æè¿°ï¼éå¸¸æ¯è¡¨æ ¼ï¼ï¼ä¾¿äºæ¥çæ°æ®ã åºæ¬æ°æ®æ¨¡åå¨å :doc:`dataset <usage/dataset>` ä¸­å®ä¹ã è¿ä¸ªåè¯å¾æ»¡è¶³ç§å­¦è§å¯åæ°æ®å¤ççè¦æ±ï¼å¹¶åå°æ¬§æ´²èªå¤©å±èµ«æ­å°å¬å±ç§å­¦ç³»ç»äº¤äºå¼åæåï¼ç¨ Java ç¼åï¼ç¨ Jython ç¼åèæ¬ï¼çæ°æ®æ¨¡åçå¯åï¼å¹¶è®¾è®¡äºå°½å¯è½å¼å®¹ç APIã ä½¿ç¨ FDI å¯ä»¥å°ä¸åæ ¼å¼çæ°æ®æåæå¸¸è§åæ¨¡ååæ°æ® ``äº§å``ï¼åæ¬æ³¨éï¼æè¿°ãç±»åãåä½ãé»è®¤å¼åæææ§è§èï¼ååæ°æ®ï¼å³äºæ°æ®çæ°æ®ï¼ã å¯ä»¥ä½¿ç¨åºæ¬æ°æ®ç»æï¼ä¾å¦åºåï¼ä¾å¦ PythonÂ ``list``ï¼ãæ å°ï¼ä¾å¦ PythonÂ ``dict``ï¼æèªå®ä¹ç±»ï¼æ¥å¶ä½äº§åçæ°ç»æè¡¨æ ¼ã FDI éç¨åµå¥åé«åº¦å¤æçç»æ 