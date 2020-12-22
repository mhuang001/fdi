

#      Dictionary of Commonly Used FITS Keywords
#
# This data dictionary contains FITS keywords that have been widely used
# within the astronomical community.  It is recommended that these
# keywords only be used as defined here.
#
# Resource: http://heasarc.gsfc.nasa.gov/docs/fcg/common_dict.html
#
FITS_keywords_HEASARC ='dict(
    # -- HIFI, see HCSS-18735',
    BAND='Band',
    # -- HERSCHEL-HSC-DOC-0662 Herschel Pointing Product Specification',
    RADESYS='raDecSys',
    AIRMASS='airMass',
    APERTURE='aperture',
    CHECKSUM='checksum',
    CHECKVER='checksumVersion',
    CONFIGUR='softwareConfiguration',
    CDELT1='cdelt1',
    CDELT2='cdelt2',
    CDELT3='cdelt3',
    CDELT4='cdelt4',
    CROTA1='crota1',
    CROTA2='crota2',
    CROTA3='crota3',
    CROTA4='crota4',
    CRPIX1='crpix1',
    CRPIX2='crpix2',
    CRPIX3='crpix3',
    CRPIX4='crpix4',
    CRVAL1='crval1',
    CRVAL2='crval2',
    CRVAL3='crval3',
    CRVAL4='crval4',
    CTYPE1='ctype1',
    CTYPE2='ctype2',
    CTYPE3='ctype3',
    CTYPE4='ctype4',
    DATAMODE='preProcessorDataMode',
    DATASUM='checksumData',
    DATE-END='endDate',
    DEC='declination',
    DEC_NOM='declinationNominal',
    DEC_OBJ='declinationObserved',
    DEC_PNT='declinationPointing',
    DEC_SCX='declinationSpacecraftX',
    DEC_SCY='declinationSpacecraftY',
    DEC_SCZ='declinationSpacecraftZ',
    DETNAM='detectorName',
    ELAPTIME='observationDuration',
    EXPOSURE='exposureTime',
    EXPTIME='exposureTime',
    FILENAME='fileName',
    FILETYPE='fileType',
    FILTER='filter',
    # -- FILTERn='',
    GRATING='grating',
    # -- GRATINGn='',
    # -- GRPIDn='',
    # -- GRPLCn='',
    # -- GRPNAME='',
    # -- HDUCLASS='',
    # -- HDUCLASn='',
    # -- HDUDOC='',
    # -- HDULEVEL='',
    # -- HDUNAME='',
    # -- HDUVER='',
    # -- HDUVERS='',
    # -- HIERARCH='',
    # -- INHERIT='',
    LATITUDE='geographicLatitude',
    LIVETIME='correctedExposureTime',
    MOONANGL='moonObservationAngle',
    # -- NEXTEND='',
    OBJNAME='objectIauName',
    OBS_ID='observationId',
    OBS_MODE='observationInstrumentMode',
    ONTIME='observationIntegrationTime',
    ORIENTAT='positionAngleAxisY',
    PA_PNT='positionAnglePointing',
    PROGRAM='softwareTaskName',
    RA='rightAscension',
    RA_NOM='rightAscensionNominal',
    RA_OBJ='rightAscensionObserved',
    RA_PNT='rightAscensionPointing',
    RA_SCX='rightAscensionSpacecraftX',
    RA_SCY='rightAscensionSpacecraftY',
    RA_SCZ='rightAscensionSpacecraftZ',
    ROOTNAME='fileRootName',
    SATURATE='dataSaturationValue',
    SUNANGLE='sunObservationAngle',
    # -- TDBINn='',
    # -- TDMAXn='',
    # -- TDMINn='',
    TELAPSE='duration',
    TIME-END='endTime',
    TIME-OBS='startTime',
    TITLE='title',
    # -- TLMAXn='',
    # -- TLMINn='',
    # -- TSORTKEY='',
    # -- WAVELN='',
    WAVELNTH='wavelnth',
    WAVEUNIT='waveunit',
)

# FITS keywords that are part of the FITS Standard definition:
#   Definition of the Flexible Image Transport System (FITS)
#   March 29, 1999
#   NOST 100-2.0
#   http://archive.stsci.edu/fits/fits_standard/
#
FITS_keywords_Standard = (
    AUTHOR='author',
    CREATOR='creator',
    DATE-OBS='startDate',
    DATE='creationDate',
    EPOCH='epoch',
    EQUINOX='equinox',
    INSTRUME='instrument',
    OBJECT='object',
    OBSERVER='observer',
    REFERENC='reference',
    TELESCOP='telescope',
)

# Dictionary of commonly used CLASS keywords
#
FITS_keywords_CLASS = dict(
    MODELNAM='modelName',
    TEMPERAT='temperature',
    MAXIS='MAXIS',
    MAXIS1='MAXIS1',
    MAXIS2='MAXIS2',
    MAXIS3='MAXIS3',
    MAXIS4='MAXIS4',
    CTYPE1='CTYPE1',
    CRVAL1='CRVAL1',
    CDELT1='CDELT1',
    CRPIX1='CRPIX1',
    CTYPE2='CTYPE2',
    CRVAL2='CRVAL2',
    CDELT2='CDELT2',
    CRPIX2='CRPIX2',
    CTYPE3='CTYPE3',
    CRVAL3='CRVAL3',
    CDELT3='CDELT3',
    CRPIX3='CRPIX3',
    CTYPE4='CTYPE4',
    CRVAL4='CRVAL4',
    CDELT4='CDELT4',
    CRPIX4='CRPIX4',
    BANDWID='BANDWID',
    RESTFREQ='RESTFREQ',
    IMAGFREQ='IMAGFREQ',
    LOFREQ='LOFREQ',
    VELOCITY='VELOCITY',
    DELTAV='DELTAV',
    BLANK='BLANK',
    OBSID='OBSID',
    APID='APID',
    BBID='BBID',
    BBTYPE='BBTYPE',
    BBNUMBER='BBNUMBER',
    SEQNUMBE='SEQNUMBE',
    BEAMEFF='BEAMEFF',
    FORWEFF='FORWEFF',
    APEREFF='APEREFF',
    ETAL='ETAL',
    ETAFSS='ETAFSS',
    ANTGAIN='ANTGAIN',
    BMAJ='BMAJ',
    BMIN='BMIN',
    BPA='BPA',
    GAINIMAG='GAINIMAG',
    TAU='TAU',
    TAUIMAGE='TAUIMAGE',
    TAUZENIT='TAUZENIT',
    MH2O='MH2O',
    HUMIDITY='HUMIDITY',
    DEWPOINT='DEWPOINT',
    PRESSURE='PRESSURE',
    TOUTSIDE='TOUTSIDE',
    WINDSPEE='WINDSPEE',
    WINDDIRE='WINDDIRE',
    SCAN='SCAN',
    SUBSCAN='SUBSCAN',
    TSYS='TSYS',
    OBSTIME='OBSTIME',
    EXPOSURE='EXPOSURE',
    DATE-OBS='DATE-OBS',
    DATE-RED='DATE-RED',
    OBJECT='OBJECT',
    LINE='LINE',
    MOLECULE='MOLECULE',
    TRANSITI='TRANSITI',
    TELESCOP='TELESCOP',
    NPHASE='NPHASE',
    DELTAF1='DELTAF1',
    PTIME1='PTIME1',
    WEIGHT1='WEIGHT1',
    DELTAF2='DELTAF2',
    PTIME2='PTIME2',
    WEIGHT2='WEIGHT2',
    THOT='THOT',
    TCOLD='TCOLD',
    OBSERVER='OBSERVER',
    PROJID='PROJID',
    OBSMODE='OBSMODE',
    TEMPSCAL='TEMPSCAL',
    TCAL='TCAL',
    TRX='TRX',
    TIMESYS='TIMESYS',
    SITELONG='SITELONG',
    SITELAT='SITELAT',
    SITEELEV='SITEELEV',
    DATAMIN='DATAMIN',
    DATAMAX='DATAMAX
)

FITS_keywords_HCSS = dict(
    # Dictionary of commonly used HCSS keywords
    #
    ACMSMODE='acmsMode',
    ACTION='action',
    ACTIVSTR='activeStrId',
    ANALYST='dataAnalyst',
    AOR='aorLabel',
    AOT='aot',
    APID='apid',
    AVERAGIN='averaging',
    BAND='band',
    BASEMOD='baselineModel',
    BASEPAR='baselineParams',
    BBCOUNT='bbCount',
    BBID='bbid',
    BBTNAME='bbTypeName',
    BBTYPE='bbType',
    BIASVOLT='biasVoltage',
    BITPOS='bitPos',
    CALFILE='calFileId',
    CALFILEV='calFileVersion',
    CALVERS='calVersion',
    CAMERA='camera',
    CAMMODEL='cameraModel',
    CD1_1='cd1_1',
    CD1_2='cd1_2',
    CD1_3='cd1_3',
    CD2_1='cd2_1',
    CD2_2='cd2_2',
    CD2_3='cd2_3',
    CD3_1='cd3_1',
    CD3_2='cd3_2',
    CD3_3='cd3_3',
    CHANGLOG='changelog',
    CHOPPLAT='chopperPlateau',
    CH_STAT='status',
    CONVELF='constVelFlag',
    CONVFACT='conversionFactor',
    CUSMODE='cusMode',
    DEC='dec',
    DEC_NOM='decNominal',
    DEC_OBJ='decObject',
    DELTAPIX='deltaPix',
    DESC='description',
    DETECTOR='arrayName',
    END_WL='endWavelength',
    ERROR='error',
    EXP_TEXT='explanatoryText',
    FINETIME='fineTime',
    FORMATV='formatVersion',
    GYROPQI='gyroPropQualIdx',
    INSTMODE='instMode',
    INTERPM='interpMethod',
    JIGGLEID='jiggleId',
    KEY_WAVE='keyWavelength',
    LEVEL='level',
    MAX_WAVE='maxWavelength',
    MIN_WAVE='minWavelength',
    MISSIONC='missionConfig',
    MODELNAM='modelName',
    NAIFID='naifId',
    NCHOPCYC='numChopCyc',
    NHIFSAA='numHifiSaa',
    NJIGGPOS='numJigglePos',
    NNODCYC='numNodCyc',
    NODCYDEN='nodCycleNum',
    NPACSSAA='numPacsSaa',
    NRASTCOL='numRasterCol',
    NRASTLIN='numRasterLines',
    NSCANLIN='numScanLines',
    NSPECTRA='numSpectra',
    NSPIRESA='numSpireSaa',
    OBJTYPE='objectType',
    OBS_ID='obsid',
    OBS_MODE='obsMode',
    OBSSTATE='obsState',
    ODNUMBER='odNumber',
    OFF_POS='offPosFlag',
    ONSRCTIM='onSourceTime',
    ONTARF='onTargetFlag',
    ORIGIN='origin',
    OUTFIELD='outOfFieldFlag',
    PC1_1='pc1_1',
    PC1_2='pc1_2',
    PC1_3='pc1_3',
    PC2_1='pc2_1',
    PC2_2='pc2_2',
    PC2_3='pc2_3',
    PC3_1='pc3_1',
    PC3_2='pc3_2',
    PC3_3='pc3_3',
    PCAVEATS='proCaveats',
    PIX_ROW='pixelRow',
    PIX_STAT='status',
    PMRA='pmRA',
    PMDEC='pmDEC',
    POINTMOD='pointingMode',
    POSANGLE='posAngle',
    PROCMODE='processingMode',
    PRODNOTE='productNotes',
    PROPOSAL='proposal',
    Q_FLAG='qualityFlag',
    RASTCOL='rasterColumnNum',
    RASTLINE='rasterLineNum',
    RA='ra',
    RADESYS='raDeSys',
    RA_ERR='raErr',
    RA_NOM='raNominal',
    RA_OBJ='raObject',
    READOUTS='readouts',
    REFEREN='references',
    REFPIXEL='refPixel',
    ROLL='roll',
    SAA='saa',
    SATURATE='saturation',
    SAT_SIGN='satValuesSigned',
    SAT_UNSG='satValuesUnsigned',
    SCANLINE='scanLineNum',
    SED_VER='sedVersion',
    SERENDIP='serendipityFlag',
    SIAM_ID='siamId',
    SKY_RES='skyResolution',
    SLEWFLAG='slewFlag',
    SLEWTIME='slewTime',
    SLICENUM='sliceNumber',
    SOURCE='source',
    SPEC_NUM='specNum',
    SPEC_RES='spectralResolution',
    SRC_DETC='sourceDetector',
    SRC_SMEC='sourceSmec',
    SRCFILE='sourceFile',
    START_WL='startWavelength',
    STATUS='state',
    STR_I_ST='strInterlacingStatus',
    STR_Q_ID='strQualIdx',
    SUBINST='subinstrumentId',
    SUBSYS='subsystem',
    TEMPERAT='temperature',
    THRESHOL='calThreshold',
    TYPE='type',
    VARIABLE='variability',
    VELDEF='velocityDefinition',
    VERSION='version',
    VER_NOTE='versionNotes',
    VFRAME='radialVelocity',
    WAVE_ID='wavelengthId',
    WAVEDESC='wavedescription',
    WAVELNTH='wavelength',
    WCS_REF='wcsReference',
    WCS_TYPE='wcsType',
    WHEELPOS='wheelPos',
    ZERO_OFF='zeroPointOffset',
    # -- ',
    # -- clean FITS TODO move',
    # -- HCSS-18608 ',
    CALBLKNO='blockNumber',
    LINECENT='lWave',
    LINES='lines',
    QUERYTME='queryTime',
    QURYTMST='queryTimeAsString',
    RANGEREP='repeatRange',
    RASSTEPL='lineStep',
    WAVEDENS='density',
    # -- HCSS-18735',
    LFREQMAX='obsFreqLsbMax',
    LFREQMIN='obsFreqLsbMin',
    LOFREQ='loFrequency',
    LODOPPAV='loFreqAvg',
    UFREQMIN='obsFreqUsbMin',
    UFREQMAX='obsFreqUsbMax',
    # -- HCSS-19017',
    SPECSYS='freqFrame',
    # -- HCSS-18514 HERSCHEL-HSC-DOC-0816 Herschel Auxiliary Products Specification',
    # -- Mission timeline summary product (auxMtls)',
    PSFVER='psfVersion',
    POSVER='posVersion',
    EPOSVER='eposVersion',
    # -- Events log product data eventsLogData',
    PKT_TYPE='packetType',
    VC='virtualChannel',
    # -- Observation request data ObsRequestData',
    OBSREQID='obsRequestId',
    OBREQVER='obsRequestVersion',
    TARGET='targetName',
    TARGTYPE='targetType',
    SUB_INST='subinstrument',
    CUS_MODE='observingMode',
    TIME_EST='timeEstimate',
    OVERHEAD='overhead',
    CHOP_ANG='chopperAngle',
    CHOPAVO1='chopperAvoidAngle1',
    CHOPAVO2='chopperAvoidAngle2',
    MAPAVOI1='mapAvoidAngle1',
    MAPAVOI2='mapAvoidAngle2',
    TSLEWMIN='timeSlewMin',
    TIH='timeInitialHold',
    TFH='timeFinalHold',
    APER_ID='apertureId',
    Y_OFFSET='yOffset',
    Z_OFFSET='zOffset',
    FIX_FRAM='fixedFrame',
    PATT='pattAngle',
    TP='timePointing',
    D1='patternD1',
    D2='patternD2',
    K_OFF='kOff',
    TOP='timeOffPointing',
    RA_OFF='raOff',
    DEC_OFF='decOff',
    SCANRATE='scanRate',
    NUM_NODS='numberNods',
    CHOPTHRO='chopperThrow',
    PATTNOD='pattNodAngle',
    TPA='timePointingA',
    TPB='timePointingB',
    TLOADMIN='timeLoadMin',
    NLOAD='numLoad',
    THOLD='timeHold',
    NHOLD='numHold',
    NRPEAT='numRepeat',
    TREPMIN='timeRepeatMin',
    NCYCLES='numCyckes',
    XRPEAT='xRepeat',
    PATTX='pattAngleX',
    NUMLINEX='numLinesX',
    D1X='patternD1X',
    D2X='patternD2X',
    NHOLDX='numHoldX',
    START_B='startAtb',
    # -- Proposal data ProposalData',
    PROPNUID='proposalNumId',
    PROPVER='propVersion',
    PROPCAT='propCategory',
    PROPSCAT='propScienceCategory',
    PROPTITL='propTitle',
    PROP_PI='propPI',
    PROPCOMM='proposerComment',
    REQTIME='requestedTime',
    TIMPRIO1='timeAllocPriority1',
    TIMPRIO2='timeAllocPriority2',
    TECHEVAL='technicalEvaluation',
    TECEVALC='technicalEvalComment',
    # -- Monitoring Data from CCUA MonitorCCUA (and Monitoring Data from CCUB MonitorCCUB)',
    RAW_SPID='rawPacketSpid',
    # -- SSO Horizons Ephemerides',
    SSO_NAME='ssoName',
    SSONAMSR='ssoNameSource',
    CEN_NAM='centerBodyName',
    CENSINAM='centerSiteName',
    CENGLONG='centerGeodeticLong',
    CENGLAT='centerGeodeticLat',
    CENGALT='centerGeodeticAlt',
    CENCLONG='centerCylindricLong',
    CENCXY='centerCylindricXY',
    CENCZ='centerCylindricZ',
    CENRADII='centerRadii',
    PERNASRC='perturberNameSource',
    OUTUNITS='outputUnits',
    REFFRAME='referenceFrame',
    OUTTYPE='outputType',
    COOSYSTM='coordinateSystem',
    ELEMDATE='elementsDate',
    ELEM_EC='elementEC',
    ELEM_QR='elementQR',
    ELEM_IN='elementIN',
    ELEM_OM='elementOM',
    ELEM_W='elementW',
    ELEM_TP='elementTP',
    ELEM_N='elementN',
    ELEM_MA='elementMA',
    ELEM_TA='elementTA',
    ELEM_A='elementA',
    ELEM_AD='elementAD',
    ELEM_PER='elementPER',
    SSO_RAD='ssoRadius',
    SSO_GM='ssoGM',
    AST_BV='asteroidColourBV',
    AST_H='asteroidH',
    AST_G='asteroidG',
    ASTROTPE='asteroidRotPeriod',
    AST_ALB='asteroridAlbedo',
    ASTSTYPE='asteroidSpectralType',
    COM_M1='cometM1',
    COM_M2='cometM2',
    COM_K1='cometK1',
    COM_K2='cometK2',
    COM_PHCO='cometPhaseCoeff',
    COM_A1='cometA1',
    COM_A2='cometA2',
    COM_A3='cometA3',
    COM_DT='cometDT',
    # -- ACMS TM Product (auxAcmsTM)',
    G1RATBIA='Gyr1RateBias',
    G1RATSCA='Gyr1RateScale',
    G123OI11='Gyr123OrientInv11',
    G123OI12='Gyr123OrientInv12',
    G123OI13='Gyr123OrientInv13',
    G123OI21='Gyr123OrientInv21',
    G123OI22='Gyr123OrientInv22',
    G123OI23='Gyr123OrientInv23',
    G123OI31='Gyr123OrientInv31',
    G123OI32='Gyr123OrientInv32',
    G123OI33='Gyr123OrientInv33',
    G124OI11='Gyr124OrientInv11',
    G124OI12='Gyr124OrientInv12',
    G124OI13='Gyr124OrientInv13',
    G124OI21='Gyr124OrientInv21',
    G124OI22='Gyr124OrientInv22',
    G124OI23='Gyr124OrientInv23',
    G124OI31='Gyr124OrientInv31',
    G124OI32='Gyr124OrientInv32',
    G124OI33='Gyr124OrientInv33',
    G134OI11='Gyr134OrientInv11',
    G134OI12='Gyr134OrientInv12',
    G134OI13='Gyr134OrientInv13',
    G134OI21='Gyr134OrientInv21',
    G134OI22='Gyr134OrientInv22',
    G134OI23='Gyr134OrientInv23',
    G134OI31='Gyr134OrientInv31',
    G134OI32='Gyr134OrientInv32',
    G134OI33='Gyr134OrientInv33',
    G2RATBIA='Gyr2RateBias',
    G2RATSCA='Gyr2RateScale',
    G234OI11='Gyr234OrientInv11',
    G234OI12='Gyr234OrientInv12',
    G234OI13='Gyr234OrientInv13',
    G234OI21='Gyr234OrientInv21',
    G234OI22='Gyr234OrientInv22',
    G234OI23='Gyr234OrientInv23',
    G234OI31='Gyr234OrientInv31',
    G234OI32='Gyr234OrientInv32',
    G234OI33='Gyr234OrientInv33',
    G3RATBIA='Gyr3RateBias',
    G3RATSCA='Gyr3RateScale',
    G4RATBIA='Gyr4RateBias',
    G4RATSCA='Gyr4RateScale',
    SCMATM11='HScmAttMan_11',
    SCMATM12='HScmAttMan_12',
    SCMATM13='HScmAttMan_13',
    SCMATM14='HScmAttMan_14',
    SCMATM21='HScmAttMan_21',
    SCMATM22='HScmAttMan_22',
    SCMATM23='HScmAttMan_23',
    SCMATM24='HScmAttMan_24',
    SCMATM31='HScmAttMan_31',
    SCMATM32='HScmAttMan_32',
    SCMATM33='HScmAttMan_33',
    SCMATM34='HScmAttMan_34',
    SCMATM41='HScmAttMan_41',
    SCMATM42='HScmAttMan_42',
    SCMATM43='HScmAttMan_43',
    SCMATM44='HScmAttMan_44',
    SCMATP11='HScmAttPoi_11',
    SCMATP12='HScmAttPoi_12',
    SCMATP13='HScmAttPoi_13',
    SCMATP14='HScmAttPoi_14',
    SCMATP21='HScmAttPoi_21',
    SCMATP22='HScmAttPoi_22',
    SCMATP23='HScmAttPoi_23',
    SCMATP24='HScmAttPoi_24',
    SCMATP31='HScmAttPoi_31',
    SCMATP32='HScmAttPoi_32',
    SCMATP33='HScmAttPoi_33',
    SCMATP34='HScmAttPoi_34',
    SCMATP41='HScmAttPoi_41',
    SCMATP42='HScmAttPoi_42',
    SCMATP43='HScmAttPoi_43',
    SCMATP44='HScmAttPoi_44',
    SCDRMA11='HScmDrifMan_11',
    SCDRMA12='HScmDrifMan_12',
    SCDRMA13='HScmDrifMan_13',
    SCDRMA14='HScmDrifMan_14',
    SCDRMA21='HScmDrifMan_21',
    SCDRMA22='HScmDrifMan_22',
    SCDRMA23='HScmDrifMan_23',
    SCDRMA24='HScmDrifMan_24',
    SCDRMA31='HScmDrifMan_31',
    SCDRMA32='HScmDrifMan_32',
    SCDRMA33='HScmDrifMan_33',
    SCDRMA34='HScmDrifMan_34',
    SCDRPO11='HScmDrifPoin_11',
    SCDRPO12='HScmDrifPoin_12',
    SCDRPO13='HScmDrifPoin_13',
    SCDRPO14='HScmDrifPoin_14',
    SCDRPO21='HScmDrifPoin_21',
    SCDRPO22='HScmDrifPoin_22',
    SCDRPO23='HScmDrifPoin_23',
    SCDRPO24='HScmDrifPoin_24',
    SCDRPO31='HScmDrifPoin_31',
    SCDRPO32='HScmDrifPoin_32',
    SCDRPO33='HScmDrifPoin_33',
    SCDRPO34='HScmDrifPoin_34',
    SCDRC101='HScmDriftrck101',
    SCDRC102='HScmDriftrck102',
    SCDRC103='HScmDriftrck103',
    SCDRC104='HScmDriftrck104',
    SCDRC105='HScmDriftrck105',
    SCDRC106='HScmDriftrck106',
    SCDRC107='HScmDriftrck107',
    SCDRC108='HScmDriftrck108',
    SCDRC109='HScmDriftrck109',
    SCDRC110='HScmDriftrck110',
    SCDRC111='HScmDriftrck111',
    SCDRC201='HScmDriftrck201',
    SCDRC202='HScmDriftrck202',
    SCDRC203='HScmDriftrck203',
    SCDRC204='HScmDriftrck204',
    SCDRC205='HScmDriftrck205',
    SCDRC206='HScmDriftrck206',
    SCDRC207='HScmDriftrck207',
    SCDRC208='HScmDriftrck208',
    SCDRC209='HScmDriftrck209',
    SCDRC210='HScmDriftrck210',
    SCDRC211='HScmDriftrck211',
    SCDRC301='HScmDriftrck301',
    SCDRC302='HScmDriftrck302',
    SCDRC303='HScmDriftrck303',
    SCDRC304='HScmDriftrck304',
    SCDRC305='HScmDriftrck305',
    SCDRC306='HScmDriftrck306',
    SCDRC307='HScmDriftrck307',
    SCDRC308='HScmDriftrck308',
    SCDRC309='HScmDriftrck309',
    SCDRC310='HScmDriftrck310',
    SCDRC311='HScmDriftrck311',
    GYMEADEL='HGyrMeasDelay',
    STROUDEL='HStrOutputDelay',
    # -- Orbit info Common Metadata',
    CENTNAME='centerName',
    # -- Orbit info TableDataset',
    INTERPDG='interpDegree',
    # -- Pointing info TableDataset',
    RSLINNUM='rasterLineNum',
    RSCOLNUM='rasterColumnNum',
    SCLINNUM='scanLineNum',
    XSCANNUM='crossScanNum',
    CUSPTNUM='customMapPointNum',
    NOD_NUM='nodCycleNum',
    ABPOSID='abPosId',
    POINTID='pointModeId',
    SEREN_FL='serendipityFlag',
    STR_USE='strInUse',
    # -- HCSS-20112 Gyro Quality Indicators',
    GYR_QUAL='gyroAttQuality',
    PROBTHRE='probThreshold',
    GYR_COV='gyroAttCoverage',
    PROB_BAD='probBad',
    COVTHRE='coverageThresh',
    GYR_SUSP='gyroAttSuspicious',
    # -- SIAM product common metadata',
    ACTSTRID='activeStrId',
    NSPIRSAA='nSpireSaa',
    NHIFISAA='nHifiSaa',
    # -- SIAM matrices - Array dataset',
    DATE-VAL='validityStart',
    # -- Calibrated detectors accumulation data CalAccumData',
    PROTONE1='protonE1',
    PROTONE2='protonE2',
    PROTONE3='protonE3',
    PROTONE4='protonE4',
    PROTONE='protonE5',
    ELECT_E1='electronE1',
    ELECT_E2='electronE2',
    ELECT_E3='electronE3',
    ELECT_E4='electronE4',
    # -- HCSS-18984 HIFI',
    LOFRQMIN='loFreqMin',
    LOFRQMAX='loFreqMax',
    FREQMIN='obsFreqMin',
    FREQMAX='obsFreqMax',
    LOFRQSTA='loFrequencyStart',
    LOFRQEND='loFrequencyEnd',
    # -- HCSS-19274 HIFI',
    IS-WBSH='wbsHscience',
    IS-WBSV='wbsVscience',
    IS-HRSH='hrsHscience',
    IS-HRSV='hrsVscience',
    REDUNDCY='redundancy',
    FREQ_THR='fsThrow',
    NOISMAXU='noiseMaxUsb',
    NOISMINU='noiseMinUsb',
    NOISMAXL='noiseMaxLsb',
    NOISMINL='noiseMinLsb',
    NOISMIND='noiseDSBMin',
    NOISMAXD='noiseDSBMax',
    NOISMINS='noiseSSBMin',
    NOISMAXS='noiseSSBMax',
    SAAMEAN='solarAspectAngleMean',
    SAARMS='solarAspectAngleRms',
    # -- HCSS-19347 HIFI',
    BACKEND='backend',
    # -- HCSS-19350 HIFI',
    NSMINWID='noiseMinWidth',
    NSMAXWID='noiseMaxWidth',
    TMBREFFQ='tmbReference',
    NSREFFRQ='noiseRefFrequency',
    TOTNSEFF='totNoiseEfficiency',
    DRFTNSCT='driftNoiseContrib',
    # -- HCSS-19348',
    ORBITFIL='orbitEphemerisSourceFile',
    # -- HCSS-19360',
    SYSSRC='redshiftFrame',
    # -- HCSS-19449',
    MIXER='mixer',
    AGEOM='aGeom',
    # -- HCSS-19358',
    TEMPSCAL='temperatureScale',
    # -- HCSS-19578',
    ETAA='apertureEfficiency',
    ETAL='forwardEff',
    ETALCAL='forwardEfficiency',
    ETAMB='beamEff',
    ETAMBCAL='mainBeamEfficiency',
    HPBW='hpbw',
    # -- HCSS-19682',
    RMSMAXU='rmsMaxUsb',
    RMSMINU='rmsMinUsb',
    RMSMAXL='rmsMaxLsb',
    RMSMINL='rmsMinLsb',
    RMSMAXS='rmsSSBMax',
    RMSMINS='rmsSSBMin',
    RMSMAXD='rmsDSBMax',
    RMSMIND='rmsDSBMin',
    # -- HCSS-19882',
    RMSNATU='rmsNativeUsb',
    RMSNATL='rmsNativeLsb',
    RMSNATS='rmsSSBNative',
    RMSNATD='rmsDSBNative',
    # -- HCSS-20388 HCSS-20389',
    NSRATIHV='rmsNoiseHV',
    NOISRATI='rmsNoise',
    # -- HCSS-20733',
    WCSNAME='wcsName',
    # -- HCSS-20497',
    LOTHRDOP='LoThrow',
    LO_THR='LoThrow_measured',
    MIXCURH='MJC_Hor',
    MIXCURV='MJC_Ver',
    OBSWPATC='OBS-patch',
    OBSWREVI='OBS-revision',
    OBSWVERS='OBS-version',
    # Note that BBNUMBER is in CLASS too',
    BBNUMBER='bbnumber',
    CBBTEMP='cbbTemp',
    HBBTEMP='hbbTemp',
    FREQRES='resolution_resampled',
    CRDER1='raError',
    CRDER2='decError',
    TCRD1='longitudeError',
    TCRD2='latitudeError',
    LSBGAIN='lsbGain',
    LSBGAIN0='lsbGain_0',
    LSBGAIN1='lsbGain_1',
    LSBGAIN2='lsbGain_2',
    LSBGAIN3='lsbGain_3',
    USBGAIN='usbGain',
    USBGAIN0='usbGain_0',
    USBGAIN1='usbGain_1',
    USBGAIN2='usbGain_2',
    USBGAIN3='usbGain_3',
    INTEGTIM='integrationTime',
    ISFOLDED='isFolded',
    SIDEBAND='sideband',
    SUBBAND='subband',
    SUBLEN1='subbandlength_1',
    SUBLEN2='subbandlength_2',
    SUBLEN3='subbandlength_3',
    SUBLEN4='subbandlength_4',
    SUBSTA1='subbandstart_1',
    SUBSTA2='subbandstart_2',
    SUBSTA3='subbandstart_3',
    SUBSTA4='subbandstart_4',
    MEDTSYS='tsys_median',
    HSOSSBVX='velocity_hso_1',
    HSOSSBVY='velocity_hso_2',
    HSOSSBVZ='velocity_hso_3',
    POSANGER='posAngleError',
    # -- Quality flags mapping',
    BADCOORD='qflag_BADCOORD_p',
    # -- Fri Jan 22 15:31:00 CET 2010',
    ADCLATCH='qflag_ADCLATCH_p',
    BSMMVSCN='qflag_BSMMVSCN_p',
    CCPOSUNC='qflag_CCPOSUNC_p',
    CCPOSUNV='qflag_CCPOSUNC_p_v',
    BATHTEMP='qflag_BATHTEMP_p',
    BATHTEMV='qflag_BATHTEMP_p_v',
    SLWBATHT='qflag_SLWBATHT_p',
    SLWBATHV='qflag_SLWBATHT_p_v',
    SSWBATHT='qflag_SSWBATHT_p',
    SSWBATHV='qflag_SSWBATHT_p_v',
    SCALTEMP='qflag_SCALTEMP_p',
    SCALTEMV='qflag_SCALTEMP_p_v',
    CAL2TEMP='qflag_CAL2TEMP_p',
    CAL2TEMV='qflag_CAL2TEMP_p_v',
    CAL4TEMP='qflag_CAL4TEMP_p',
    CAL4TEMV='qflag_CAL4TEMP_p_v',
    TEL1TEMP='qflag_TEL1TEMP_p',
    TEL1TEMV='qflag_TEL1TEMP_p_v',
    TEL2TEMP='qflag_TEL2TEMP_p',
    TEL2TEMV='qflag_TEL2TEMP_p_v',
    TEL3TEMP='qflag_TEL3TEMP_p',
    TEL3TEMV='qflag_TEL3TEMP_p_v',
    DDROPPED='qflag_DDROPPED_p',
    DDROPPEV='qflag_DDROPPED_p_v',
    TLINESNR='qflag_TLINESNR_p',
    TLINESNV='qflag_TLINESNR_p_v',
    DFLUXPLW='qflag_DFLUXPLW_p',
    DFLUXPLV='qflag_DFLUXPLW_p_v',
    DFLUXPMW='qflag_DFLUXPMW_p',
    DFLUXPMV='qflag_DFLUXPMW_p_v',
    DFLUXPSW='qflag_DFLUXPSW_p',
    DFLUXPSV='qflag_DFLUXPSW_p_v',
    MPLWFAIL='qflag_MPLWFAIL_p',
    MPMWFAIL='qflag_MPMWFAIL_p',
    MPSWFAIL='qflag_MPSWFAIL_p',
    MPLWMAXI='qflag_MPLWMAXI_p',
    MPMWMAXI='qflag_MPMWMAXI_p',
    MPSWMAXI='qflag_MPSWMAXI_p',
    DLATMWLW='qflag_DLATMWLW_p',
    DLATMWLV='qflag_DLATMWLW_p_v',
    DLATSWLW='qflag_DLATSWLW_p',
    DLATSWLV='qflag_DLATSWLW_p_v',
    DLATSWMW='qflag_DLATSWMW_p',
    DLATSWMV='qflag_DLATSWMW_p_v',
    DLONMWLW='qflag_DLONMWLW_p',
    DLONMWLV='qflag_DLONMWLW_p_v',
    DLONSWLW='qflag_DLONSWLW_p',
    DLONSWLV='qflag_DLONSWLW_p_v',
    DLONSWMW='qflag_DLONSWMW_p',
    DLONSWMV='qflag_DLONSWMW_p_v',
    MFAILPLW='qflag_MFAILPLW_p',
    MFAILPLV='qflag_MFAILPLW_p_v',
    MFAILPMW='qflag_MFAILPMW_p',
    MFAILPMV='qflag_MFAILPMW_p_v',
    MFAILPSW='qflag_MFAILPSW_p',
    MFAILPSV='qflag_MFAILPSW_p_v',
    MISFRING='qflag_MISFRING_p',
    MISFRINV='qflag_MISFRING_p_v',
    NFITSPLW='qflag_NFITSPLW_p',
    NFITSPMW='qflag_NFITSPMW_p',
    NFITSPSW='qflag_NFITSPSW_p',
    PLWVOLK3='qflag_PLWVOLK3_p',
    PLWVOLKV='qflag_PLWVOLK3_p_v',
    PMWVOLK3='qflag_PMWVOLK3_p',
    PMWVOLKV='qflag_PMWVOLK3_p_v',
    PSWVOLK3='qflag_PSWVOLK3_p',
    PSWVOLKV='qflag_PSWVOLK3_p_v',
    SLWVOLK3='qflag_SLWVOLK3_p',
    SLWVOLKV='qflag_SLWVOLK3_p_v',
    SSWVOLK3='qflag_SSWVOLK3_p',
    SSWVOLKV='qflag_SSWVOLK3_p_v',
    BSMCHPSL='qflag_BSMCHPSL_p',
    BSMCHPSV='qflag_BSMCHPSL_p_v',
    BSMJGGSL='qflag_BSMJGGSL_p',
    BSMJGGSV='qflag_BSMJGGSL_p_v',
    SLWCLIPN='qflag_SLWCLIPN_p',
    SLWCLIPV='qflag_SLWCLIPN_p_v',
    SSWCLIPN='qflag_SSWCLIPN_p',
    SSWCLIPV='qflag_SSWCLIPN_p_v',
    NMISSPOS='qflag_NMISSPOS_p',
    NMISSPOV='qflag_NMISSPOS_p_v',
    SLWGLITN='qflag_SLWGLITN_p',
    SLWGLITV='qflag_SLWGLITN_p_v',
    SSWGLITN='qflag_SSWGLITN_p',
    SSWGLITV='qflag_SSWGLITN_p_v',
    SLWPHASE='qflag_SLWPHASE_p',
    SLWPHASV='qflag_SLWPHASE_p_v',
    SSWPHASE='qflag_SSWPHASE_p',
    SSWPHASV='qflag_SSWPHASE_p_v',
    FDIFFPLW='qflag_FDIFFPLW_p',
    FDIFFPLV='qflag_FDIFFPLW_p_v',
    FDIFFPMW='qflag_FDIFFPMW_p',
    FDIFFPMV='qflag_FDIFFPMW_p_v',
    FDIFFPSW='qflag_FDIFFPSW_p',
    FDIFFPSV='qflag_FDIFFPSW_p_v',
    PLWNEGFL='qflag_PLWNEGFL_p',
    PMWNEGFL='qflag_PMWNEGFL_p',
    PSWNEGFL='qflag_PSWNEGFL_p',
    DPOSPLWC='qflag_DPOSPLWC_p',
    DPOSPLWV='qflag_DPOSPLWC_p_v',
    DPOSPMWC='qflag_DPOSPMWC_p',
    DPOSPMWV='qflag_DPOSPMWC_p_v',
    DPOSPSWC='qflag_DPOSPSWC_p',
    DPOSPSWV='qflag_DPOSPSWC_p_v',
    DPOSMWLW='qflag_DPOSMWLW_p',
    DPOSMWLV='qflag_DPOSMWLW_p_v',
    DPOSSWLW='qflag_DPOSSWLW_p',
    DPOSSWLV='qflag_DPOSSWLW_p_v',
    DPOSSWMW='qflag_DPOSSWMW_p',
    DPOSSWMV='qflag_DPOSSWMW_p_v',
    HTHERPLW='qflag_HTHERPLW_p',
    HTHERPLV='qflag_HTHERPLW_p_v',
    HTHERPMW='qflag_HTHERPMW_p',
    HTHERPMV='qflag_HTHERPMW_p_v',
    HTHERPSW='qflag_HTHERPSW_p',
    HTHERPSV='qflag_HTHERPSW_p_v',
    HTHERSLW='qflag_HTHERSLW_p',
    HTHERSLV='qflag_HTHERSLW_p_v',
    HTHERSSW='qflag_HTHERSSW_p',
    HTHERSSV='qflag_HTHERSSW_p_v',
    INVTIMES='qflag_INVTIMES_p',
    INVTIMEV='qflag_INVTIMES_p_v',
    JOUTPLW='qflag_JOUTPLW_p',
    JOUTPLV='qflag_JOUTPLW_p_v',
    JOUTPMW='qflag_JOUTPMW_p',
    JOUTPMV='qflag_JOUTPMW_p_v',
    JOUTPSW='qflag_JOUTPSW_p',
    JOUTPSV='qflag_JOUTPSW_p_v',
    NOUTPLW='qflag_NOUTPLW_p',
    NOUTPLV='qflag_NOUTPLW_p_v',
    NOUTPMW='qflag_NOUTPMW_p',
    NOUTPMV='qflag_NOUTPMW_p_v',
    NOUTPSW='qflag_NOUTPSW_p',
    NOUTPSV='qflag_NOUTPSW_p_v',
    PLWGL1L='qflag_PLWGL1L_p',
    PLWGL1V='qflag_PLWGL1L_p_v',
    PMWGL1L='qflag_PMWGL1L_p',
    PMWGL1V='qflag_PMWGL1L_p_v',
    PSWGL1L='qflag_PSWGL1L_p',
    PSWGL1V='qflag_PSWGL1L_p_v',
    PLWGL2L='qflag_PLWGL2L_p',
    PLWGL2V='qflag_PLWGL2L_p_v',
    PMWGL2L='qflag_PMWGL2L_p',
    PMWGL2V='qflag_PMWGL2L_p_v',
    PSWGL2L='qflag_PSWGL2L_p',
    PSWGL2V='qflag_PSWGL2L_p_v',
    PLWOOCAL='qflag_PLWOOCAL_p',
    PLWOOCAV='qflag_PLWOOCAL_p_v',
    PMWOOCAL='qflag_PMWOOCAL_p',
    PMWOOCAV='qflag_PMWOOCAL_p_v',
    PSWOOCAL='qflag_PSWOOCAL_p',
    PSWOOCAV='qflag_PSWOOCAL_p_v',
    SLWOOCAL='qflag_SLWOOCAL_p',
    SLWOOCAV='qflag_SLWOOCAL_p_v',
    SSWOOCAL='qflag_SSWOOCAL_p',
    SSWOOCAV='qflag_SSWOOCAL_p_v',
    SLWRAT1L='qflag_SLWRAT1L_p',
    SLWRAT1V='qflag_SLWRAT1L_p_v',
    SSWRAT1L='qflag_SSWRAT1L_p',
    SSWRAT1V='qflag_SSWRAT1L_p_v',
    SLWRAT2L='qflag_SLWRAT2L_p',
    SLWRAT2V='qflag_SLWRAT2L_p_v',
    SSWRAT2L='qflag_SSWRAT2L_p',
    SSWRAT2V='qflag_SSWRAT2L_p_v',
    SLWIDENT='qflag_SLWIDENT_p',
    SLWIDENV='qflag_SLWIDENT_p_v',
    SSWIDENT='qflag_SSWIDENT_p',
    SSWIDENV='qflag_SSWIDENT_p_v',
    SLWDIFFR='qflag_SLWDIFFR_p',
    SLWDIFFV='qflag_SLWDIFFR_p_v',
    SSWDIFFR='qflag_SSWDIFFR_p',
    SSWDIFFV='qflag_SSWDIFFR_p_v',
    SLWOUTLR='qflag_SLWOUTLR_p',
    SLWOUTLV='qflag_SLWOUTLR_p_v',
    SSWOUTLR='qflag_SSWOUTLR_p',
    SSWOUTLV='qflag_SSWOUTLR_p_v',
    RATTRUNC='qflag_RATTRUNC_p',
    RATTRUNV='qflag_RATTRUNC_p_v',
    RATTRPLW='qflag_RATTRPLW_p',
    RATTRPLV='qflag_RATTRPLW_p_v',
    RATTRPMW='qflag_RATTRPMW_p',
    RATTRPMV='qflag_RATTRPMW_p_v',
    RATTRPSW='qflag_RATTRPSW_p',
    RATTRPSV='qflag_RATTRPSW_p_v',
    RATTRSLW='qflag_RATTRSLW_p',
    RATTRSLV='qflag_RATTRSLW_p_v',
    RATTRSSW='qflag_RATTRSSW_p',
    RATTRSSV='qflag_RATTRSSW_p_v',
    PHASEWRP='qflag_PHASEWRP_p',
    PHASEWRV='qflag_PHASEWRP_p_v',
    RETSPLIN='qflag_RETSPLIN_p',
    SCANEXTR='qflag_SCANEXTR_p',
    SCANEXTV='qflag_SCANEXTR_p_v',
    SMECTEMP='qflag_SMECTEMP_p',
    SMECTEMV='qflag_SMECTEMP_p_v',
    AVGNGPSU='qflag_AVGNGPSU_p',
    AVGNGPSV='qflag_AVGNGPSU_p_v',
    AVNODPSU='qflag_AVNODPSU_p',
    AVNODPSV='qflag_AVNODPSU_p_v',
    NODPSU='qflag_NODPSU_p',
    NODPSV='qflag_NODPSU_p_v',
    AVGSPEED='qflag_AVGSPEED_p',
    AVGSPEEV='qflag_AVGSPEED_p_v',
    STDSPEED='qflag_STDSPEED_p',
    STDSPEEV='qflag_STDSPEED_p_v',
    WRBSESLW='qflag_WRBSESLW_p',
    WRBSESLV='qflag_WRBSESLW_p_v',
    WRBSESSW='qflag_WRBSESSW_p',
    WRBSESSV='qflag_WRBSESSW_p_v',
    BPSPUBUF='qflag_BPSPUBUF_p',
    BPSPUBUV='qflag_BPSPUBUF_p_v',
    BPSPUMIS='qflag_BPSPUMIS_p',
    BPSPUMIV='qflag_BPSPUMIS_p_v',
    BPSPUFAI='qflag_BPSPUFAI_p',
    BPSPUFAV='qflag_BPSPUFAI_p_v',
    RPSPUBUF='qflag_RPSPUBUF_p',
    RPSPUBUV='qflag_RPSPUBUF_p_v',
    RPSPUMIS='qflag_RPSPUMIS_p',
    RPSPUMIV='qflag_RPSPUMIS_p_v',
    RPSPUFAI='qflag_RPSPUFAI_p',
    RPSPUFAV='qflag_RPSPUFAI_p_v',
    BPSCISAT='qflag_BPSCISAT_p',
    BPSCISAV='qflag_BPSCISAT_p_v',
    RPSCISAT='qflag_RPSCISAT_p',
    RPSCISAV='qflag_RPSCISAT_p_v',
    BPCALSAT='qflag_BPCALSAT_p',
    BPCALSAV='qflag_BPCALSAT_p_v',
    RPCALSAT='qflag_RPCALSAT_p',
    RPCALSAV='qflag_RPCALSAT_p_v',
    BPSCGLIT='qflag_BPSCGLIT_p',
    BPSCGLIV='qflag_BPSCGLIT_p_v',
    RPSCGLIT='qflag_RPSCGLIT_p',
    RPSCGLIV='qflag_RPSCGLIT_p_v',
    BPCAGLIT='qflag_BPCAGLIT_p',
    BPCAGLIV='qflag_BPCAGLIT_p_v',
    RPCAGLIT='qflag_RPCAGLIT_p',
    RPCAGLIV='qflag_RPCAGLIT_p_v',
    POINTACC='qflag_POINTACC_p',
    POINTACV='qflag_POINTACC_p_v',
    POINTSTA='qflag_POINTSTA_p',
    POINTSTV='qflag_POINTSTA_p_v',
    POINTOFF='qflag_POINTOFF_p',
    POINTOFV='qflag_POINTOFF_p_v',
    BPSCNUMF='qflag_BPSCNUMF_p',
    BPSCNUMV='qflag_BPSCNUMF_p_v',
    BPSCRMSF='qflag_BPSCRMSF_p',
    BPSCRMSV='qflag_BPSCRMSF_p_v',
    BPSCVALF='qflag_BPSCVALF_p',
    BPSCVALV='qflag_BPSCVALF_p_v',
    BPSCVRMF='qflag_BPSCVRMF_p',
    BPSCVRMV='qflag_BPSCVRMF_p_v',
    RPSCNUMF='qflag_RPSCNUMF_p',
    RPSCNUMV='qflag_RPSCNUMF_p_v',
    RPSCRMSF='qflag_RPSCRMSF_p',
    RPSCRMSV='qflag_RPSCRMSF_p_v',
    RPSCVALF='qflag_RPSCVALF_p',
    RPSCVALV='qflag_RPSCVALF_p_v',
    RPSCVRMF='qflag_RPSCVRMF_p',
    RPSCVRMV='qflag_RPSCVRMF_p_v',
    BPCANUMF='qflag_BPCANUMF_p',
    BPCANUMV='qflag_BPCANUMF_p_v',
    BPCARMSF='qflag_BPCARMSF_p',
    BPCARMSV='qflag_BPCARMSF_p_v',
    BPCAVALF='qflag_BPCAVALF_p',
    BPCAVALV='qflag_BPCAVALF_p_v',
    BPCAVRMF='qflag_BPCAVRMF_p',
    BPCAVRMV='qflag_BPCAVRMF_p_v',
    RPCANUMF='qflag_RPCANUMF_p',
    RPCANUMV='qflag_RPCANUMF_p_v',
    RPCARMSF='qflag_RPCARMSF_p',
    RPCARMSV='qflag_RPCARMSF_p_v',
    RPCAVALF='qflag_RPCAVALF_p',
    RPCAVALV='qflag_RPCAVALF_p_v',
    RPCAVRMF='qflag_RPCAVRMF_p',
    RPCAVRMV='qflag_RPCAVRMF_p_v',
    BPVALPIX='qflag_BPVALPIX_p',
    BPVALPIV='qflag_BPVALPIX_p_v',
    RPVALPIX='qflag_RPVALPIX_p',
    RPVALPIV='qflag_RPVALPIX_p_v',
    BPOBSTRU='qflag_BPOBSTRU_p',
    BPOBSTRV='qflag_BPOBSTRU_p_v',
    RPOBSTRU='qflag_RPOBSTRU_p',
    RPOBSTRV='qflag_RPOBSTRU_p_v',
    BPSUBBCK='qflag_BPSUBBCK_p',
    BPSUBBCV='qflag_BPSUBBCK_p_v',
    RPSUBBCK='qflag_RPSUBBCK_p',
    RPSUBBCV='qflag_RPSUBBCK_p_v',
    FSPUBLUE='qflag_FSPUBLUE_p',
    FSPUBLUV='qflag_FSPUBLUE_p_v',
    FSPURED='qflag_FSPURED_p',
    FSPUREV='qflag_FSPURED_p_v',
    NOQDC='qflag_NOQDC_p',
    FASTQDC='qflag_FASTQDC_p',
    NOPOWCOR='qflag_NOPOWCOR_p',
    FPUMIXC='qflag_FPUMIXC_p',
    FPUMIXCV='qflag_FPUMIXCV_p',
    FPUMIXV='qflag_FPUMIXV_p',
    FPUMIXMC='qflag_FPUMIXMC_p',
    FPUMIXMR='qflag_FPUMIXMR_p',
    FPUCHOP='qflag_FPUCHOP_p',
    FPUDPLX='qflag_FPUDPLX_p',
    FPULNA='qflag_FPULNA_p',
    FPUTMPH='qflag_FPUTMPH_p',
    FPUTMPC='qflag_FPUTMPC_p',
    FPUTMPL0='qflag_FPUTMPL0_p',
    SPUR='qflag_SPUR_p',
    POINTFAL='qflag_POINTFAL_p',
    CHCKCOMB='qflag_CHCKCOMB_p',
    CHCKZERO='qflag_CHCKZERO_p',
    SPIKENUM='qflag_SPIKENUM_p',
    SPIKENUV='qflag_SPIKENUM_p_v',
    BADPIXEL='qflag_BADPIXEL_p',
    BADPIXEV='qflag_BADPIXEL_p_v',
    SATPIXEL='qflag_SATPIXEL_p',
    SATPIXEV='qflag_SATPIXEL_p_v',
    OBSMODE='qflag_OBSMODE_i',
    MAXDRIFT='qflag_MAXDRIFT_p',
    FREQCHEC='qflag_FREQCHEC_p',
    CHOPATT='qflag_CHOPATT_p',
    CHOPVAL='qflag_CHOPVAL_p',
    LOFPATT='qflag_LOFPATT_p',
    LOFVAL='qflag_LOFVAL_p',
    LOFVAV='qflag_LOFVAL_p_v',
    BUFFPATT='qflag_BUFFPATT_p',
    BUFFVAL='qflag_BUFFVAL_p',
    BUFFVAV='qflag_BUFFVAL_p_v',
    PHASCHEC='qflag_PHASCHEC_p',
    HOTCOLD='qflag_HOTCOLD_p',
    TSYSFLAG='qflag_TSYSFLAG_p',
    INTENCAL='qflag_INTENCAL_p',
    NWEIGHTS='qflag_NWEIGHTS_p',
    NOSUBST='qflag_NOSUBST_p',
    NOBASELN='qflag_NOBASELN_p',
    ONOFFSEQ='qflag_ONOFFSEQ_p',
    ONOFFLEN='qflag_ONOFFLEN_p',
    ONOFFPRO='qflag_ONOFFPRO_p',
    NOFFSUBS='qflag_NOFFSUBS_p',
    UNALIGHK='qflag_UNALIGHK_p',
    UNALIGHV='qflag_UNALIGHK_p_v',
    NOCHOPHK='qflag_NOCHOPHK_p',
    NOCHOPHV='qflag_NOCHOPHK_p_v',
    NOCOMMHK='qflag_NOCOMMHK_p',
    NOCOMMHV='qflag_NOCOMMHK_p_v',
    NOFREQHK='qflag_NOFREQHK_p',
    NOFREQHV='qflag_NOFREQHK_p_v',
    NOLOCOFF='qflag_NOLOCOFF_p',
    NOLOCOFV='qflag_NOLOCOFF_p_v',
    NOLOCOMA='qflag_NOLOCOMA_p',
    NOLOCOMV='qflag_NOLOCOMA_p_v',
    BBIDCORR='qflag_BBIDCORR_p',
    BBIDCORV='qflag_BBIDCORR_p_v',
    DFORDER='qflag_DFORDER_p',
    LESSDATA='qflag_LESSDATA_p',
    MOREDATA='qflag_MOREDATA_p',
    RTERROR='qflag_RTERROR_p',
    RTERROV='qflag_RTERROR_p_v',
    CMDFAIL='qflag_CMDFAIL_p',
    CMDFAIV='qflag_CMDFAIL_p_v',
    TMLOSSES='qflag_TMLOSSES_p',
    MIB='qflag_MIB_p',
    EVENT='qflag_EVENT_p',
    EXCPTION='qflag_EXCPTION_p',
    ALARM='qflag_ALARM_p',
    TCERRORS='qflag_TCERRORS_p',
    SPOINTIN='qflag_SPOINTIN_p',
    POINTING='qflag_POINTING_p',
    DEGLITB='qflag_BSSCGLIT_p',
    DEGLITBV='qflag_BSSCGLIT_p_v',
    DEGLITR='qflag_RSSCGLIT_p',
    DEGLITRV='qflag_RSSCGLIT_p_v',
    ANOMY70='qflag_DMANOG1_p',
    ANOMY70V='qflag_DMANOG1_p_v',
    LOWPNTS='qflag_SLOWSAMP_p',
    LOWPNTSV='qflag_SLOWSAMP_p_v',
    NUMPIXB='qflag_BSVALPIX_p',
    NUMPIXBV='qflag_BSVALPIX_p_v',
    NUMPIXRB='qflag_RSVALPIX_p_v',
    NUMPIXR='qflag_RSVALPIX_p',
    SATUR_B='qflag_BSSCISAT_p',
    SATUR_BV='qflag_BSSCISAT_p_v',
    SATUR_R='qflag_RSSCISAT_p',
    SATUR_RV='qflag_RSSCISAT_p_v',
    # HCSS-20946',
    ANOMLPTG='qflag_ANOMLPTG_p',
    BADDATDC='qflag_BADDATDC_p',
    BADDATL2='qflag_BADDATL2_p',
    BADHCDC='qflag_BADHCDC_p',
    CALERR='qflag_CALERR_p',
    CHKSINZR='qflag_CHKSINZR_p',
    DARKSATR='qflag_DARKSATR_p',
    DECONF='qflag_DECONF_p',
    FPUDPLXC='qflag_FPUDPLXC_p',
    GYRATTSP='qflag_GYRATTSP_p',
    HD247194='qflag_HD247194_p',
    HEBHAPPL='qflag_HEBHAPPL_p',
    HEBVAPPL='qflag_HEBVAPPL_p',
    HECRZERO='qflag_HECRZERO_p',
    HM025193='qflag_HM025193_i',
    HM029191='qflag_HM029191_i',
    HM120191='qflag_HM120191_i',
    HRSHASIC='qflag_HRSHASIC_p',
    HRSVASIC='qflag_HRSVASIC_p',
    HSDFAIL='qflag_HSDFAIL_p',
    LOTUNING='qflag_LOTUNING_p',
    LOUCUR='qflag_LOUCUR_p',
    LOUDSB='qflag_LOUDSB_p',
    LOUDSB1B='qflag_LOUDSB1B_p',
    LRGTHROW='qflag_LRGTHROW_p',
    NOFRQCAL='qflag_NOFRQCAL_p',
    NOVELOC='qflag_NOVELOC_p',
    PLTFRMNG='qflag_PLTFRMNG_p',
    RMSHV='qflag_RMSHV_p',
    RMSHVVST='qflag_RMSHVVST_p',
    RMSNOISE='qflag_RMSNOISE_p',
    SCANCNT='qflag_SCANCNT_p',
    UNKBB='qflag_UNKBB_p',
    WM409565='qflag_WM409565_i',
    WM508565='qflag_WM508565_i',
    WM608565='qflag_WM608565_i',
    WRGFRQSC='qflag_WRGFRQSC_i',
    WRONGAVG='qflag_WRONGAVG_p',
    ZEROINCF='qflag_ZEROINCF_p',
    # HCSS-20580, 2015-09-01',
    NRASTER='numPoints',
    NLINES='numLines',
    # HCSS-21199',
    PS3_0='ps3_0',
    PS3_1='ps3_1',
    PS3_2='ps3_2',
    # HCSS-21442',
    ETAAH='apertureEfficiency_H',
    ETAAV='apertureEfficiency_V',
    ETAMBH='beamEff_H',
    ETAMBV='beamEff_V',
    UPCONVH='upConvert_H',
    UPCONVV='upConvert_V',
    SKREFCON='skyRefContam',
    SKREFCOR='skyRefContamCorr',
    ICREATOR='iccCreator',
    # HCSS-21442',
    REFZEROV='zeroVelocityReference',
    VELALGO='computeVelocityAlgorithm',
    AREAPIX='areaPixels',
    AREAAS='areaArcsecs',
    ROWCENT='regionParameter_centerRow',
    COLCENT='regionParameter_centerCol',
    ROWRAD='regionParameter_radiusRow',
    COLRAD='regionParameter_radiuscol',
    ROWSTART='regionParameter_row1',
    ROWEND='regionParameter_row2',
    COLSTART='regionParameter_col1',
    COLEND='regionParameter_col2',
    CDESC3='cdesc3',
    FLIPYX='flipxy',
    ATTQUATR='attitudeQuaternion',
    CHOP='Chopper',
    BB_TYPE='bbtype',
    NCHANNEL='channels',
    CMDCHOP='cmd_chopper',
    PRIMERED='prime_redundant',
    LOFMEAS='LoFrequency_measured',
    FRQWIDTH='frequencyWidth',
    FRQMONIT='frequency_monitor',
    LOFTHROW='loThrow',
    CHKCOMB='checkComb',
    COMBRES='resolution',
    RES='resolution',
    GAINMETH='gainMethod',
    LOADINT='loadInterval',
    BEAMUSED='beamUsed',
    PIXELSIZ='pixelSize',
    MAPSIZE='mapSize',
    REFPIX='refPixelCoordinates',
    PIXOFFS='pixelOffset',
    FLYANGLE='flyAngle',
    HPBWUSED='hpbwAssumed',
    MAPWIDGR='mapWidthGridded',
    MAPHEIGR='mapHeightGridded',
    MAPWIDOB='mapWidthObserved',
    MAPHEIOB='mapHeightObserved',
    HEBCORRV='hebCorrVApplied',
    HEBCORRH='hebCorrHApplied',
    NDATASET='count_ds',
    ERPFLAG='erpFlagged',
    # HCSS-21520',
    GAINFLAG='gain_flag',
    SPURREJC='spur_rejection',
    STARTCOL='startCol',
    ENDCOL='endCol',
    STARTROW='startRow',
    ENDROW='endRow',
    ASPCTRAT='aspectRatio',
    SLITWID='slitWidth',
    ROWMIN='rowMin',
    ROWMAX='rowMax',
    COLMIN='colMin',
    COLMAX='colMax',
)

# Dictionary of commonly used HCSS keywords that follow a numbering pattern
# e.g. OBSID123='obsid123, PROP1='proposal1
FITS_keywords_Numbered = dict(
    OBSID='obsid',
    PROP='proposal',
    CUNIT='cunit',
    CONSNAM='constraintName',
    CONSTYP='constraintType',
    CONSINF='constraintInfo',
    CONS_ST='timeConstraintStart',
    CONS_EN='timeConstraintEnd',
    YARRAY='yArray',
    ZARRAY='zArray',
    PROCOI='propCoI',
    PERTNAM='perturberName',
    PERTGM='perturberGM',
    CALTBC='calTableComment',
    # -- HCSS-19602 Deconvolution task',
    LOF='loFreq',
    NBD='num_bad_chan_in_scan',
    BSC='bad_scan',
    POBS_='photObsid',
)

FITS_KEYWORDS = copy.copy(FITS_keywords_Standard)
FITS_KEYWORDS.update(FITS_keywords_HEASARC)
