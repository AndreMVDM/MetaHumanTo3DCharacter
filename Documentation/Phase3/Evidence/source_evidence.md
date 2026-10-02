# Installed source evidence

Excerpts retain original one-based line numbers. Source paths and SHA-256 identify the inspected installation. No Unreal API was executed.

## S01

[Build.version](<D:/Epic Games/UE_5.8/Engine/Build/Build.version>): D:\Epic Games\UE_5.8\Engine\Build\Build.version

    1: {
    2: 	"MajorVersion": 5,
    3: 	"MinorVersion": 8,
    4: 	"PatchVersion": 3,
    5: 	"Changelist": 58210709,
    6: 	"CompatibleChangelist": 55116800,
    7: 	"IsLicenseeVersion": 0,
    8: 	"IsPromotedBuild": 1,
    9: 	"BranchName": "++UE5+Release-5.8"
    10: }

## S02

[MetaHumanCharacterEditorSubsystem.h](<D:/Epic Games/UE_5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter/Source/MetaHumanCharacterEditor/Public/MetaHumanCharacterEditorSubsystem.h>): D:\Epic Games\UE_5.8\Engine\Plugins\MetaHuman\MetaHumanCharacter\Source\MetaHumanCharacterEditor\Public\MetaHumanCharacterEditorSubsystem.h

    490: UCLASS(BlueprintType)
    491: class METAHUMANCHARACTEREDITOR_API UMetaHumanCharacterEditorSubsystem
    492: 	: public UEditorSubsystem
    493: 	, public FTickableEditorObject
    494: {
    495: 	GENERATED_BODY()
    496: 
    497: public:
    498: 
    499: 	//~FTickableEditorObject interface
    500: 	virtual bool IsTickable() const override;
    501: 	virtual void Tick(float InDeltaTime) override;
    502: 	virtual TStatId GetStatId() const override;
    503: 	//~End of FTickableEditorObject interface
    504: 
    505: public:
    506: 	//
    507: 	// Subsystem Initialization
    508: 	//
    509: 	//~Begin USubsystem interface
    510: 	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    511: 	//~End USubsystem interface
    512: 
    513: 	/**
    514: 	 * Utility for obtaining a pointer to the global instance of this subsystem in the editor.
    515: 	 */
    516: 	static UMetaHumanCharacterEditorSubsystem* Get();
    517: 
    518: 	/**
    519: 	 * Registers an object to be edited. The first object registered will
    520: 	 * also load the Texture Synthesis model to make it to be used
    521: 	 * 
    522: 	 * Most functions taking a Character on this class require the Character to be registered for
    523: 	 * editing first.
    524: 	 * 
    525: 	 * Call RemoveObjectToEdit when done editing. If TryAddObjectToEdit returns false, the 
    526: 	 * Character is not registered, so there's no need to call RemoveObjectToEdit.
    527: 	 */
    528: 	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Initialization")
    529: 	[[nodiscard]] bool TryAddObjectToEdit(UMetaHumanCharacter* InCharacter);
    530: 
    531: 	/** Returns true if the object is registered for editing */
    532: 	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "MetaHuman|Initialization")
    533: 	bool IsObjectAddedForEditing(const UMetaHumanCharacter* InCharacter) const;
    534: 
    535: 	/**
    536: 	 * Tells the subsystem that a character is no longer being edited.
    537: 	 * Unloads the texture synthesis model when the last object being
    538: 	 * edited is removed from the subsystem
    539: 	 */
    540: 	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Initialization")
    541: 	void RemoveObjectToEdit(const UMetaHumanCharacter* InCharacter);
    542: 
    543: 	/**
    544: 	* Clears all internal model data for Texture Synthesis and re-loads the model using the path in the settings
    545: 	*/
    546: 	void ResetTextureSynthesis();
    547: 
    548: 	/**
    549: 	 * Returns the Collection used to build the Character's preview.
    550: 	 *

    1345: 	void AutoRigFace(TNotNull<UMetaHumanCharacter*> InCharacter, const UE::MetaHuman::ERigType InRigType);
    1346: 
    1347: 	/**
    1348: 	 * @brief Make a request to auto-rig a character
    1349: 	 *
    1350: 	 * Requires the character to be added for edit using TryAddObjectToEdit
    1351: 	 *
    1352: 	 * @param InCharacter The character to be auto-rigged
    1353: 	 * @param InParams Parameters to control the auto-rigging process
    1354: 	 */
    1355: 	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Auto-Rigging")
    1356: 	void RequestAutoRigging(UMetaHumanCharacter* InCharacter, const FMetaHumanCharacterAutoRiggingRequestParams& InParams = FMetaHumanCharacterAutoRiggingRequestParams());
    1357: 

    1653: 	/**
    1654: 	 * @brief Fits the Character body state to the conformed mesh of the input asset, which must be a SkelMesh or Static Mesh which has the correct number of vertices.
    1655: 	 * 	 
    1656: 	 * @param InMetaHumanCharacter The character to import the body template mesh to
    1657: 	 * @param InTemplateMesh The mesh (either StaticMesh or SkelMesh) which much match the topology of a MetaHuman body or combined head and body mesh
    1658: 	 * @param InBodyFitOptions the fitting options used during the fitting process
    1659: 	 * @return code indicating success or failure
    1660: 	 */
    1661: 	UE_DEPRECATED(5.7, "ImportFromBodyTemplate option has been deprecatd. Please use ConformBody, SetBodyJointTranslations, SetBodyMesh or ImportWholeRig.")
    1662: 	EImportErrorCode ImportFromBodyTemplate(UMetaHumanCharacter* InMetaHumanCharacter, UObject* InTemplateMesh, EMetaHumanCharacterBodyFitOptions InBodyFitOptions);
    1663: #endif // WITH_EDITORONLY_DATA
    1664: 
    1665: 	/**
    1666: 	 * Get the mesh for performing import from body template 
    1667: 	 */
    1668: 	EImportErrorCode GetMeshForBodyConforming(UMetaHumanCharacter* InMetaHumanCharacter, UObject* InBodyTemplateMesh, UObject* InHeadTemplateMesh, bool bInMatchVerticesByUVs, TArray<FVector3f>& OutVertices);
    1669: 
    1670: 	/**
    1671: 	 * @brief Blueprint exposed version of the GetMeshForBodyConforming function
    1672: 	 *
    1673: 	 * @param InMetaHumanCharacter The character to import the body template mesh to
    1674: 	 * @param InBodyTemplateMesh The mesh (either StaticMesh or SkelMesh) which much match the topology of a MetaHuman body or combined head and body mesh	 
    1675: 	 * @param InHeadTemplateMesh The mesh (either StaticMesh or SkelMesh) which much match the topology of a MetaHuman head mesh
    1676: 	 * @param bInMatchVerticesByUVs flag which if set to true uses UV matching to match the vertices, otherwise requires exactly matching SkelMesh
    1677: 	 * @param OutVertices On completion contains the body mesh vertices
    1678: 	 * @return code indicating success or failure
    1679: 	 */
    1680: 	UE_DEPRECATED(5.8, "Use GetMeshForBodyConformingFromTemplate instead.")
    1681: 	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Conforming", meta = (DeprecatedFunction, DeprecationMessage = "Use GetMeshForBodyConformingFromTemplate instead."))
    1682: 	EImportErrorCode GetMeshForBodyConforming(UMetaHumanCharacter* InMetaHumanCharacter, UObject* InBodyTemplateMesh, UObject* InHeadTemplateMesh, bool bInMatchVerticesByUVs, TArray<FVector>& OutVertices);
    1683: 
    1684: 	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Conforming")
    1685: 	EImportErrorCode GetMeshForBodyConformingFromTemplate(UMetaHumanCharacter* InMetaHumanCharacter, UObject* InBodyTemplateMesh, UObject* InHeadTemplateMesh, bool bInMatchVerticesByUVs, TArray<FVector3f>& OutVertices);
    1686: 
    1687: 	
    1688: 	/**
    1689: 	 * Get the mesh for performing import from body template
    1690: 	 */
    1691: 	EImportErrorCode GetMeshForBodyConforming(UMetaHumanCharacter* InMetaHumanCharacter, TSharedRef<IDNAReader> BodyDNA, TSharedPtr<IDNAReader> HeadDNA, TArray<FVector3f>& OutVertices);
    1692: 	
    1693: 	/**
    1694: 	 * Get the body mesh vertices for conforming, from DNA file paths.
    1695: 	 *
    1696: 	 * @param InMetaHumanCharacter  The character to conform
    1697: 	 * @param InBodyDnaFilePath     Absolute file path to the body DNA file
    1698: 	 * @param InHeadDnaFilePath     Absolute file path to the head DNA file (optional, pass empty string to omit)
    1699: 	 * @param OutVertices           On success, contains the body mesh vertices
    1700: 	 * @return EImportErrorCode::Success on success, otherwise an error code describing the failure
    1701: 	 */
    1702: 	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Conforming")
    1703: 	EImportErrorCode GetMeshForBodyConformingFromDNA(UMetaHumanCharacter* InMetaHumanCharacter, const FString& InBodyDnaFilePath, const FString& InHeadDnaFilePath, TArray<FVector3f>& OutVertices);
    1704: 
    1705: 	/**
    1706: 	 * Get the joints for performing import from body template
    1707: 	 */
    1708: 	EImportErrorCode GetJointsForBodyConforming(USkeletalMesh* InTemplateMesh, TArray<FVector3f>& OutJointWorldTranslations, TArray<FVector3f>& OutJointRotations);
    1709: 
    1710: 	/**
    1711: 	 * @brief Blueprint exposed version of the GetJointsForBodyConforming function
    1712: 	 *
    1713: 	 * @param InTemplateMesh The mesh to be conformed which much match the topology of a MetaHuman body or combined head and body mesh
    1714: 	 * @param OutJointWorldTranslations On completion contains the body joint world translations
    1715: 	 * @param OutJointRotations On completion contains the body joint rotations
    1716: 	 * @return code indicating success or failure
    1717: 	 */
    1718: 	UE_DEPRECATED(5.8, "Use GetJointsForBodyConformingFromTemplate instead.")
    1719: 	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Conforming", meta = (DeprecatedFunction, DeprecationMessage = "Use GetJointsForBodyConformingFromTemplate instead."))
    1720: 	EImportErrorCode GetJointsForBodyConforming(USkeletalMesh* InTemplateMesh, TArray<FVector>& OutJointWorldTranslations, TArray<FVector>& OutJointRotations);
    1721: 
    1722: 	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Conforming")
    1723: 	EImportErrorCode GetJointsForBodyConformingFromTemplate(USkeletalMesh* InTemplateMesh, TArray<FVector3f>& OutJointWorldTranslations, TArray<FVector3f>& OutJointRotations);
    1724: 
    1725: 
    1726: 	/**
    1727: 	 * Get the joints for performing import from body template
    1728: 	 */
    1729: 	EImportErrorCode GetJointsForBodyConforming(TSharedRef<IDNAReader> BodyDNA, TArray<FVector3f>& OutJointWorldTranslations, TArray<FVector3f>& OutJointRotations);
    1730: 
    1731: 	/**
    1732: 	 * Get the body joint data for conforming, from a DNA file path.
    1733: 	 * Suitable for use from Python and Blueprints.
    1734: 	 *
    1735: 	 * @param InBodyDnaFilePath             Absolute file path to the body DNA file
    1736: 	 * @param OutJointWorldTranslations     On success, contains the body joint world translations
    1737: 	 * @param OutJointRotations             On success, contains the body joint rotations
    1738: 	 * @return EImportErrorCode::Success on success, otherwise an error code describing the failure
    1739: 	 */
    1740: 	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Conforming")
    1741: 	EImportErrorCode GetJointsForBodyConformingFromDNA(const FString& InBodyDnaFilePath, TArray<FVector3f>& OutJointWorldTranslations, TArray<FVector3f>& OutJointRotations);
    1742: 	
    1743: 	/* Conforms the body mesh to target parameters */
    1744: 	bool ConformBody(UMetaHumanCharacter* InMetaHumanCharacter, const TArray<FVector3f>& InVertices, const TArray<FVector3f>& InJointRotations, bool bTargetIsInAPose, bool bEstimateJointsFromMesh);

    1786: 	/* Conforms the body and head meshes to target meshes */
    1787: 	bool ConformTargetMeshesAsync(TNotNull<UMetaHumanCharacter*> InMetaHumanCharacter, const FMetaHumanCharacterTargetMeshKey& InTargetMeshKey, const FConformTargetParams& InConformTargetParams, bool bBlocking = false);
    1788: 
    1789: 	/** Extract topology vertices and triangle indices from a static or skeletal mesh.
    1790: 	 * Uses the MeshDescription to return the same data that the interactive conform tool uses internally.
    1791: 	 * @param InMesh The source mesh (UStaticMesh or USkeletalMesh)
    1792: 	 * @param OutVertices Topology vertex positions
    1793: 	 * @param OutTriangleIndices Triangle indices (3 per triangle, referencing OutVertices)
    1794: 	 * @return true if extraction succeeded
    1795: 	 */
    1796: 	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Conforming")
    1797: 	static bool GetMeshDataForConforming(UObject* InMesh, TArray<FVector3f>& OutVertices, TArray<int32>& OutTriangleIndices);
    1798: 
    1799: 	/** Synchronously conforms the body and head meshes to target parameters.
    1800: 	 * Python/Blueprint-friendly wrapper around ConformTargetMeshesAsync that
    1801: 	 * runs with bBlocking=true and returns the solver result.
    1802: 	 * @param InMetaHumanCharacter The character to conform. Must be open for editing.
    1803: 	 * @param InTargetMeshKey Identifies which target mesh slot (body / head / combined) the
    1804: 	 *                       conform applies to. Used as the per-mesh key for target-pose state
    1805: 	 *                       storage so successive conforms against different meshes don't
    1806: 	 *                       overwrite each other.
    1807: 	 * @param InConformTargetParams Solver inputs: target mesh data, keypoints, face tracking, solver settings.
    1808: 	 * @return true if the conform solver succeeded; false on invalid input or solve failure.
    1809: 	 */
    1810: 	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Conforming")
    1811: 	bool ConformToTargetMeshes(UMetaHumanCharacter* InMetaHumanCharacter, const FMetaHumanCharacterTargetMeshKey& InTargetMeshKey, const FConformTargetParams& InConformTargetParams);
    1812: 
    1813: 	/** Run face landmark detection on an image and return tracking contour curves.
    1814: 	 * Use with a front-facing portrait of the target mesh — typically a SceneCapture2D
    1815: 	 * render. The first call after editor start synchronously loads the face contour
    1816: 	 * tracker NNE models (the default tracker asset), so it can take several seconds;
    1817: 	 * subsequent calls hit the cached models and are fast.
    1818: 	 * @param InImageData Raw pixel data (BGRA8); length must equal InWidth * InHeight.
    1819: 	 * @param InWidth Image width in pixels.
    1820: 	 * @param InHeight Image height in pixels.
    1821: 	 * @param OutCurveTrackingPoints Named contour curves (2D points in image space).
    1822: 	 * @return true if any landmarks were detected; false on invalid input, model load failure, or no face found.
    1823: 	 */
    1824: 	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Conforming")
    1825: 	bool TrackFaceLandmarksFromImage(const TArray<FColor>& InImageData, int32 InWidth, int32 InHeight, TMap<FString, FTrackingPoints>& OutCurveTrackingPoints);
    1826: 
    1827: 	/* Rigidly aligns the character state to the target meshes */
    1828: 	bool AlignToTargetMeshesAsync(TNotNull<UMetaHumanCharacter*> InMetaHumanCharacter, const FMetaHumanCharacterTargetMeshKey& InTargetMeshKey, const FConformTargetParams& InConformTargetParams, bool bBlocking = false);
    1829: 	
    1830: 	/** After conforming body state in pose, finalizes body and face states by evaluating solved body state in MetaHuman A Pose, and updating face state from it.
    1831: 	 */
    1832: 	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Conforming")
    1833: 	void CommitPosedStateAsAPose(UMetaHumanCharacter* InMetaHumanCharacter, const FMetaHumanCharacterTargetMeshKey& InTargetMeshKey);
    1834: 
    1835: 	/** Synchronously aligns tthe body and head meshes to target meshes 
    1836: 	 * Python/Blueprint-friendly wrapper that calls AlignToTargetMeshesAsync in blocking mode.
    1837: 	 */
    1838: 	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Conforming")
    1839: 	bool AlignToTargetMeshes(UMetaHumanCharacter* InMetaHumanCharacter, const FMetaHumanCharacterTargetMeshKey& InTargetMeshKey, const FConformTargetParams& InConformTargetParams);

    1888: 	UE_DEPRECATED(5.8, "Use ConformBodyToTarget instead.")
    1889: 	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Conforming", meta = (DeprecatedFunction, DeprecationMessage = "Use ConformBodyToTarget instead."))
    1890: 	bool ConformBody(UMetaHumanCharacter* InMetaHumanCharacter, const TArray<FVector>& InVertices, const TArray<FVector>& InJointRotations, bool bRepose, bool bEstimateJointsFromMesh);
    1891: 
    1892: 	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Conforming")
    1893: 	bool ConformBodyToTarget(UMetaHumanCharacter* InMetaHumanCharacter, const TArray<FVector3f>& InVertices, const TArray<FVector3f>& InJointRotations, bool bTargetIsInAPose, bool bEstimateJointsFromMesh);
    1894: 
    1895: 	/* Set custom body joints */
    1896: 	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Conforming")
    1897: 	bool SetBodyJoints(UMetaHumanCharacter* InMetaHumanCharacter, const TArray<FVector3f>& InComponentJointTranslations, const TArray<FVector3f>& InJointRotations, bool bImportHelperJoints);
    1898: 
    1899: 	/* Set custom body neutral mesh */ 
    1900: 	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Conforming")
    1901: 	bool SetBodyMesh(UMetaHumanCharacter* InMetaHumanCharacter, const TArray<FVector3f>& InVertices, bool bRepositionHelperJoints);
    1902: 
    1903: 	/* Import body as a fully rigged Character  from DNA, sets character to a fixed body type */
    1904: 	EImportErrorCode ImportBodyWholeRig(TNotNull<UMetaHumanCharacter*> InMetaHumanCharacter, TSharedRef<class IDNAReader> InBodyDna, TSharedPtr<IDNAReader> InHeadDna);
    1905: 
    1906: 	/* Import body as a fully rigged Character from DNA file paths, sets character to a fixed body type */
    1907: 	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Conforming")
    1908: 	EImportErrorCode ImportBodyWholeRig(UMetaHumanCharacter* InMetaHumanCharacter, const FString& InBodyDnaFilePath, const FString& InHeadDnaFilePath);
    1909: #if WITH_EDITORONLY_DATA
    1910: 	/**
    1911: 	 * Fit the state to the supplied body DNA. Returns true if successful, false otherwise
    1912: 	 */
    1913: 	UE_DEPRECATED(5.7, "FitToBodyDna option has been deprecatd. Please use ConformBodyFromDna with FConformBodyParams instead.")
    1914: 	bool FitToBodyDna(TNotNull<UMetaHumanCharacter*> InCharacter, TSharedRef<class IDNAReader> InBodyDna, EMetaHumanCharacterBodyFitOptions InBodyFitOptions);
    1915: #endif // WITH_EDITORONLY_DATA
    1916: 
    1917: 	/**
    1918: 	 * @brief Gets the list of body constrains from the underlying parametric body model
    1919: 	 * 
    1920: 	 * Requires the character to be added for edit using TryAddObjectToEdit
    1921: 	 * 
    1922: 	 * @param InCharacter the character to retrieve the body constraints for
    1923: 	 * @param bScaleMeasurementRangesWithHeight scale the measurement ranges by height to help stay within realistic model proportions
    1924: 	 * @return the list of body constraints provided by the underlying parametric body model
    1925: 	 */
    1926: 	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Sculpting")
    1927: 	TArray<FMetaHumanCharacterBodyConstraint> GetBodyConstraints(const UMetaHumanCharacter* InCharacter, bool bScaleMeasurementRangesWithHeight = false) const;
    1928: 
    1929: 	/**
    1930: 	 * @brief Set body constraints and evaluate the parametric body
    1931: 	 * 
    1932: 	 * Requires the character to be added for edit using TryAddObjectToEdit
    1933: 	 * 
    1934: 	 * @param InCharacter The character to update the constraints
    1935: 	 * @param InBodyContrains The list of body constraints to apply to the character
    1936: 	 */
    1937: 	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Sculpting")
    1938: 	void SetBodyConstraints(const UMetaHumanCharacter* InCharacter, const TArray<FMetaHumanCharacterBodyConstraint>& InBodyConstraints);
    1939: 

## S03

[MetaHumanCharacterEditorSubsystem.cpp](<D:/Epic Games/UE_5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter/Source/MetaHumanCharacterEditor/Private/MetaHumanCharacterEditorSubsystem.cpp>): D:\Epic Games\UE_5.8\Engine\Plugins\MetaHuman\MetaHumanCharacter\Source\MetaHumanCharacterEditor\Private\MetaHumanCharacterEditorSubsystem.cpp

    7408: EImportErrorCode UMetaHumanCharacterEditorSubsystem::GetMeshForBodyConforming(UMetaHumanCharacter* InMetaHumanCharacter, UObject* InBodyTemplateMesh, UObject* InHeadTemplateMesh, bool bInMatchVerticesByUVs, TArray<FVector3f>& OutVertices)
    7409: {
    7410: 	OutVertices.Empty();
    7411: #if WITH_EDITOR
    7412: 	
    7413: 	if (!IsValid(InMetaHumanCharacter) || !IsValid(InBodyTemplateMesh))
    7414: 	{
    7415: 		
    7416: 		UE_LOGF(LogMetaHumanCharacterEditor, Error, "Metahuman character or body template not provided.");
    7417: 		return EImportErrorCode::GeneralError;
    7418: 	}
    7419: 	TSharedPtr<IDNAReader> BodyDnaReader = FMetaHumanCharacterSkelMeshUtils::GetArchetypeDNAAsset(EMetaHumanImportDNAType::Body, GetTransientPackage())->GetDNAReader();
    7420: 	TSharedPtr<IDNAReader> CombinedDnaReader = FMetaHumanCharacterSkelMeshUtils::GetArchetypeDNAAsset(EMetaHumanImportDNAType::Combined, GetTransientPackage())->GetDNAReader();
    7421: 	TSharedPtr<IDNAReader> HeadDnaReader = FMetaHumanCharacterSkelMeshUtils::GetArchetypeDNAAsset(EMetaHumanImportDNAType::Face, GetTransientPackage())->GetDNAReader();
    7422: 	if (!BodyDnaReader || !CombinedDnaReader)
    7423: 	{
    7424: 		UE_LOGF(LogMetaHumanCharacterEditor, Error, "Failed to get archetype DNA reader");
    7425: 		return EImportErrorCode::GeneralError;
    7426: 	}
    7427: 	const int32 Template2MHLODIndex = 0;
    7428: 	const int32 DNAArchetypeMeshIndex = 0;
    7429: 	const int32 NumHeadMeshVertices = HeadDnaReader->GetVertexPositionCount(0);
    7430: 	const int32 NumBodyMeshVertices = BodyDnaReader->GetVertexPositionCount(0); 
    7431: 	const int32 NumCombinedBodyMeshVertices = CombinedDnaReader->GetVertexPositionCount(0);
    7432: 
    7433: 	if (USkeletalMesh* TemplateSkeletalMesh = Cast<USkeletalMesh>(InBodyTemplateMesh))
    7434: 	{
    7435: 		if (FDNAToSkelMeshMap* DNAToSkelMeshMap = USkelMeshDNAUtils::CreateMapForUpdatingNeutralMesh(BodyDnaReader.Get(), TemplateSkeletalMesh))
    7436: 		{
    7437: 			if (bInMatchVerticesByUVs)
    7438: 			{
    7439: 				if (!FMetaHumanCharacterSkelMeshUtils::GetUVCorrespondingSkeletalMeshVertices(TemplateSkeletalMesh, Template2MHLODIndex, DNAToSkelMeshMap, BodyDnaReader, DNAArchetypeMeshIndex, OutVertices))
    7440: 				{
    7441: 					return EImportErrorCode::InvalidInputData;
    7442: 				}
    7443: 			}
    7444: 			else
    7445: 			{
    7446: 				if (!FMetaHumanCharacterSkelMeshUtils::GetSkeletalMeshVertices(TemplateSkeletalMesh, Template2MHLODIndex, DNAToSkelMeshMap, DNAArchetypeMeshIndex, OutVertices))
    7447: 				{
    7448: 					return EImportErrorCode::InvalidInputData;
    7449: 				}
    7450: 			}
    7451: 		}
    7452: 		else
    7453: 		{
    7454: 			UE_LOGF(LogMetaHumanCharacterEditor, Error, "Failed to create DNA to skel mesh map");
    7455: 			return EImportErrorCode::GeneralError;
    7456: 		}
    7457: 	}
    7458: 	else if (UStaticMesh* TemplateStaticMesh = Cast<UStaticMesh>(InBodyTemplateMesh))
    7459: 	{
    7460: 		TArray<FVector3f> CurVertices;
    7461: 		if (bInMatchVerticesByUVs)
    7462: 		{
    7463: 			if (FMetaHumanCharacterSkelMeshUtils::GetUVCorrespondingStaticMeshVertices(TemplateStaticMesh, Template2MHLODIndex, BodyDnaReader, DNAArchetypeMeshIndex, CurVertices))
    7464: 			{
    7465: 				OutVertices = CurVertices;
    7466: 			}
    7467: 			else
    7468: 			{
    7469: 				return EImportErrorCode::InvalidInputData;
    7470: 			}
    7471: 		}
    7472: 		else
    7473: 		{
    7474: 			int32 NumMeshVertices = UE::MetaHuman::GetNumberOfVertices(TemplateStaticMesh, Template2MHLODIndex);
    7475: 			if (NumMeshVertices != NumBodyMeshVertices && NumMeshVertices != NumCombinedBodyMeshVertices)
    7476: 			{
    7477: 				return EImportErrorCode::InvalidInputData;
    7478: 			}
    7479: 
    7480: 			if (FMetaHumanCharacterSkelMeshUtils::GetStaticMeshVertices(TemplateStaticMesh, Template2MHLODIndex, CurVertices))
    7481: 			{
    7482: 				OutVertices = CurVertices;
    7483: 			}
    7484: 			else
    7485: 			{
    7486: 				return EImportErrorCode::InvalidInputData;
    7487: 			}
    7488: 		}
    7489: 	}
    7490: 	else
    7491: 	{
    7492: 		UE_LOGF(LogMetaHumanCharacterEditor, Error, "Failed to get data for conforming as Template Mesh is invalid");
    7493: 		return EImportErrorCode::InvalidInputData;
    7494: 	}
    7495: 
    7496: 	if (USkeletalMesh* TemplateSkeletalMesh = Cast<USkeletalMesh>(InHeadTemplateMesh))
    7497: 	{
    7498: 		if (FDNAToSkelMeshMap* DNAToSkelMeshMap = USkelMeshDNAUtils::CreateMapForUpdatingNeutralMesh(HeadDnaReader.Get(), TemplateSkeletalMesh))
    7499: 		{
    7500: 				TArray<FVector3f> CurVertices;
    7501: 				if (bInMatchVerticesByUVs)
    7502: 				{
    7503: 					if (!FMetaHumanCharacterSkelMeshUtils::GetUVCorrespondingSkeletalMeshVertices(TemplateSkeletalMesh, Template2MHLODIndex, DNAToSkelMeshMap, HeadDnaReader, 0, CurVertices))
    7504: 					{
    7505: 						return EImportErrorCode::InvalidInputData;
    7506: 					}
    7507: 				}
    7508: 				else
    7509: 				{
    7510: 					if (!FMetaHumanCharacterSkelMeshUtils::GetSkeletalMeshVertices(TemplateSkeletalMesh, Template2MHLODIndex, DNAToSkelMeshMap, 0, CurVertices))
    7511: 					{
    7512: 						return EImportErrorCode::InvalidInputData;
    7513: 					}
    7514: 				}
    7515: 				
    7516: 			//We want to combine head and mesh into one mesh, OutVertices already contains body
    7517: 			TArray<int32> Mapping = GetOrCreateCharacterIdentity(InMetaHumanCharacter->TemplateType).Body->GetBodyToCombinedMapping();
    7518: 			CurVertices.SetNumUninitialized(CombinedDnaReader->GetVertexPositionCount(0));
    7519: 			for (int32 i = 0; i < Mapping.Num(); ++i)
    7520: 			{
    7521: 				CurVertices[Mapping[i]] = OutVertices[i];	
    7522: 			}
    7523: 			OutVertices = CurVertices;
    7524: 		}
    7525: 		else
    7526: 		{
    7527: 			UE_LOGF(LogMetaHumanCharacterEditor, Error, "Failed to create DNA to skel mesh map");
    7528: 			return EImportErrorCode::GeneralError;
    7529: 		}
    7530: 	} else if (UStaticMesh* TemplateStaticMesh = Cast<UStaticMesh>(InHeadTemplateMesh))
    7531: 	{
    7532: 		TArray<FVector3f> CurVertices;
    7533: 		if (bInMatchVerticesByUVs)
    7534: 		{
    7535: 			if (!FMetaHumanCharacterSkelMeshUtils::GetUVCorrespondingStaticMeshVertices(TemplateStaticMesh, Template2MHLODIndex, HeadDnaReader, DNAArchetypeMeshIndex, CurVertices))
    7536: 			{
    7537: 				return EImportErrorCode::InvalidInputData;
    7538: 			}
    7539: 		}
    7540: 		else
    7541: 		{
    7542: 			int32 NumMeshVertices = UE::MetaHuman::GetNumberOfVertices(TemplateStaticMesh, Template2MHLODIndex);
    7543: 			if (NumMeshVertices != NumHeadMeshVertices)
    7544: 			{
    7545: 				return EImportErrorCode::InvalidInputData;
    7546: 			}
    7547: 
    7548: 			if (!FMetaHumanCharacterSkelMeshUtils::GetStaticMeshVertices(TemplateStaticMesh, Template2MHLODIndex, CurVertices))
    7549: 			{
    7550: 				return EImportErrorCode::InvalidInputData;
    7551: 			}
    7552: 		}
    7553: 		//We want to combine head and mesh into one mesh, OutVertices already contains body
    7554: 		TArray<int32> Mapping = GetOrCreateCharacterIdentity(InMetaHumanCharacter->TemplateType).Body->GetBodyToCombinedMapping();
    7555: 		CurVertices.SetNumUninitialized(CombinedDnaReader->GetVertexPositionCount(0));
    7556: 		for (int32 i = 0; i < Mapping.Num(); ++i)
    7557: 		{
    7558: 			CurVertices[Mapping[i]] = OutVertices[i];	
    7559: 		}
    7560: 		OutVertices = CurVertices;
    7561: 	}
    7562: 
    7563: #endif
    7564: 
    7565: 	return EImportErrorCode::Success;
    7566: }
    7567: 
    7568: /* Conforms the body mesh to target parameters */
    7569: bool UMetaHumanCharacterEditorSubsystem::ConformBody(UMetaHumanCharacter* InMetaHumanCharacter, const TArray<FVector3f>& InVertices, const TArray<FVector3f>& InJointRotations, bool bTargetIsInAPose, bool bEstimateJointsFromMesh)
    7570: {
    7571: 	if (!IsValid(InMetaHumanCharacter))
    7572: 	{
    7573: 		UE_LOGFMT(LogMetaHumanCharacterEditor, Error, "ConformBody called with invalid character");
    7574: 		return false;
    7575: 	}
    7576: 	TSharedRef<FMetaHumanCharacterBodyIdentity::FState> BodyState = CopyBodyState(InMetaHumanCharacter);
    7577: 	if (BodyState->Conform(InVertices, InJointRotations, bTargetIsInAPose, bEstimateJointsFromMesh))
    7578: 	{
    7579: 		CommitBodyState(InMetaHumanCharacter, BodyState);
    7580: 		return true;
    7581: 	}
    7582: 	return false;
    7583: }
    7584: 
    7585: bool UMetaHumanCharacterEditorSubsystem::FitFaceStateFromBodyWithEyesTeethTemplate(UMetaHumanCharacter* InMetaHumanCharacter,
    7586: 	UObject* InTeethMesh,
    7587: 	UObject* InLeftEyeMesh,
    7588: 	UObject* InRightEyeMesh,
    7589: 	bool bInMatchVerticesByUVs)
    7590: {

    7740: bool UMetaHumanCharacterEditorSubsystem::ConformTargetMeshesAsync(TNotNull<UMetaHumanCharacter*> InMetaHumanCharacter,
    7741: 	const FMetaHumanCharacterTargetMeshKey& InTargetMeshKey,
    7742: 	const FConformTargetParams& InConformTargetParams,
    7743: 	bool bBlocking)
    7744: {
    7745: 	if (!IsValid(InMetaHumanCharacter))
    7746: 	{
    7747: 		UE_LOGFMT(LogMetaHumanCharacterEditor, Error, "Error conforming to target body: Invalid MetaHuman character");
    7748: 		return false;
    7749: 	}
    7750: 	
    7751: 	FMetaHumanCharacterEditorMeshImportContext& MeshImportContext = CharacterMeshImportContexts.FindOrAdd(InMetaHumanCharacter);
    7752: 	if (!MeshImportContext.MeshImportTaskRunner)
    7753: 	{
    7754: 		MeshImportContext.MeshImportTaskRunner = FMeshImportTaskRunner::Create();
    7755: 	}
    7756: 
    7757: 	// Captured by the OnMeshImportFinish lambda below so the bBlocking caller
    7758: 	// can return the actual solver result instead of hardcoded true. Use a
    7759: 	// TWeakObjectPtr for the character so we don't dereference a dangling
    7760: 	// pointer if the character is GC'd before the async task completes.
    7761: 	TSharedRef<bool, ESPMode::ThreadSafe> BlockingSuccess = MakeShared<bool, ESPMode::ThreadSafe>(false);
    7762: 	TWeakObjectPtr<UMetaHumanCharacter> WeakCharacter = InMetaHumanCharacter;
    7763: 
    7764: 	MeshImportContext.MeshImportTaskRunner->OnMeshImportIteration().BindUObject(this, &UMetaHumanCharacterEditorSubsystem::OnMeshImportIterationUpdate, InMetaHumanCharacter);
    7765: 	MeshImportContext.MeshImportTaskRunner->OnMeshImportFinish().BindLambda(
    7766: 		[this, WeakCharacter, BlockingSuccess](bool bSuccess, bool bWasCancelled,
    7767: 			const TSharedRef<FMetaHumanCharacterBodyIdentity::FState>& InBodyState,
    7768: 			const TSharedRef<FMetaHumanCharacterIdentity::FState>& InFaceState,
    7769: 			const FMetaHumanCharacterTargetMeshKey& InTargetMeshKey)
    7770: 		{
    7771: 			*BlockingSuccess = bSuccess;
    7772: 			if (UMetaHumanCharacter* Character = WeakCharacter.Get())
    7773: 			{
    7774: 				OnMeshImportComplete(bSuccess, bWasCancelled, InBodyState, InFaceState, InTargetMeshKey, Character);
    7775: 			}
    7776: 		});
    7777: 
    7778: 	MeshImportContext.MeshImportProgressHandle = FSlateNotificationManager::Get().StartProgressNotification(LOCTEXT("MeshSolveProgress", "Mesh-Solving"), InConformTargetParams.BodyConformSolveSettings.Iterations + InConformTargetParams.BodyConformSolveSettings.FaceIterations);
    7779: 	MeshImportContext.MeshImportNotificationItem = UE::MetaHuman::ShowNotification(LOCTEXT("StartMeshImportMessage", "Solving Mesh"), SNotificationItem::ECompletionState::CS_Pending, /* InExpireDuration */ 3.5f,
    7780: 		FSimpleDelegate::CreateUObject(this, &UMetaHumanCharacterEditorSubsystem::CancelMeshAsyncProcess, InMetaHumanCharacter));
    7781: 
    7782: 	TSharedRef<FMetaHumanCharacterEditorData> CharacterData = CharacterDataMap[InMetaHumanCharacter];
    7783: 	
    7784: 	TSharedPtr<IDNAReader> ArchetypeDnaReader = FMetaHumanCharacterSkelMeshUtils::GetArchetypeDNAAsset(EMetaHumanImportDNAType::Body, GetTransientPackage())->GetDNAReader();
    7785: 	CharacterData->BodyDnaToSkelMeshMap->MapJoints(ArchetypeDnaReader.Get());
    7786: 	
    7787: 	MeshImportContext.MeshImportTaskRunner->StartConform(CharacterData->BodyState,
    7788: 		CharacterData->FaceState,
    7789: 		InTargetMeshKey,
    7790: 		InConformTargetParams);
    7791: 	
    7792: 	InMetaHumanCharacter->NotifyRiggingStateChanged();
    7793: 
    7794: 	if (bBlocking)
    7795: 	{
    7796: 		UE::MetaHuman::WaitForAsyncTask([this, InMetaHumanCharacter]
    7797: 											{
    7798: 												return IsAsyncConformPending(InMetaHumanCharacter);
    7799: 											});
    7800: 		return *BlockingSuccess;
    7801: 	}
    7802: 
    7803: 	return true;
    7804: }
    7805: 

    8136: bool UMetaHumanCharacterEditorSubsystem::ConformToTargetMeshes(UMetaHumanCharacter* InMetaHumanCharacter, const FMetaHumanCharacterTargetMeshKey& InTargetMeshKey, const FConformTargetParams& InConformTargetParams)
    8137: {
    8138: 	if (!IsValid(InMetaHumanCharacter))
    8139: 	{
    8140: 		UE_LOGFMT(LogMetaHumanCharacterEditor, Error, "ConformToTargetMeshes: invalid character");
    8141: 		return false;
    8142: 	}
    8143: 	if (!IsObjectAddedForEditing(InMetaHumanCharacter))
    8144: 	{
    8145: 		UE_LOGFMT(LogMetaHumanCharacterEditor, Error, "ConformToTargetMeshes: character {Character} is not added for editing", InMetaHumanCharacter->GetName());
    8146: 		return false;
    8147: 	}
    8148: 	// Delegate to the async path with bBlocking=true. ConformTargetMeshesAsync
    8149: 	// captures bSuccess across the async boundary and returns it from the
    8150: 	// blocking branch, so we get the actual solver result here.
    8151: 	return ConformTargetMeshesAsync(TNotNull<UMetaHumanCharacter*>(InMetaHumanCharacter), InTargetMeshKey, InConformTargetParams, /*bBlocking=*/true);
    8152: }

    8211: bool UMetaHumanCharacterEditorSubsystem::GetMeshDataForConforming(UObject* InMesh, TArray<FVector3f>& OutVertices, TArray<int32>& OutTriangleIndices)
    8212: {
    8213: 	OutVertices.Empty();
    8214: 	OutTriangleIndices.Empty();
    8215: 
    8216: 	if (!IsValid(InMesh))
    8217: 	{
    8218: 		UE_LOGFMT(LogMetaHumanCharacterEditor, Error, "GetMeshDataForConforming: invalid mesh");
    8219: 		return false;
    8220: 	}
    8221: 
    8222: 	FMeshDescription* MeshDescription = nullptr;
    8223: 	constexpr int32 LODIndex = 0;
    8224: 	if (UStaticMesh* StaticMesh = Cast<UStaticMesh>(InMesh))
    8225: 	{
    8226: 		MeshDescription = StaticMesh->GetMeshDescription(LODIndex);
    8227: 	}
    8228: 	else if (USkeletalMesh* SkeletalMesh = Cast<USkeletalMesh>(InMesh))
    8229: 	{
    8230: 		MeshDescription = SkeletalMesh->GetMeshDescription(LODIndex);
    8231: 	}
    8232: 
    8233: 	if (!MeshDescription)
    8234: 	{
    8235: 		UE_LOGFMT(LogMetaHumanCharacterEditor, Error, "GetMeshDataForConforming: could not get MeshDescription from {Mesh}", InMesh->GetName());
    8236: 		return false;
    8237: 	}
    8238: 
    8239: 	if (MeshDescription->NeedsCompact())
    8240: 	{
    8241: 		FElementIDRemappings IDRemappings;
    8242: 		MeshDescription->Compact(IDRemappings);
    8243: 	}
    8244: 
    8245: 	// Extract topology vertex positions
    8246: 	TVertexAttributesConstRef<FVector3f> Positions = MeshDescription->GetVertexPositions();
    8247: 	OutVertices.Reserve(MeshDescription->Vertices().Num());
    8248: 	for (const FVertexID VertexID : MeshDescription->Vertices().GetElementIDs())
    8249: 	{
    8250: 		OutVertices.Add(Positions[VertexID]);
    8251: 	}
    8252: 
    8253: 	// Extract triangle indices
    8254: 	for (const FTriangleID TriangleID : MeshDescription->Triangles().GetElementIDs())
    8255: 	{
    8256: 		TArrayView<const FVertexID> TriVertexIDs = MeshDescription->GetTriangleVertices(TriangleID);
    8257: 		OutTriangleIndices.Add(TriVertexIDs[0].GetValue());
    8258: 		OutTriangleIndices.Add(TriVertexIDs[1].GetValue());
    8259: 		OutTriangleIndices.Add(TriVertexIDs[2].GetValue());
    8260: 	}
    8261: 
    8262: 	return true;
    8263: }
    8264: 

## S04

[MetaHumanCharacterBodyIdentity.cpp](<D:/Epic Games/UE_5.8/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib/Source/MetaHumanCoreTechLib/Private/MetaHumanCharacterBodyIdentity.cpp>): D:\Epic Games\UE_5.8\Engine\Plugins\MetaHuman\MetaHumanCoreTechLib\Source\MetaHumanCoreTechLib\Private\MetaHumanCharacterBodyIdentity.cpp

    234: 	bool ValidateConformTargetMesh(const FConformTargetMesh& InConformTargetMesh)
    235: 	{
    236: 		if (InConformTargetMesh.TargetPartsType == ETargetPartsType::HeadOnly || InConformTargetMesh.TargetPartsType == ETargetPartsType::HeadAndBody)
    237: 		{
    238: 			if (InConformTargetMesh.HeadVertices.IsEmpty() || InConformTargetMesh.HeadVertexIndices.IsEmpty())
    239: 			{
    240: 				UE_LOGF(LogMetaHumanCoreTechLib, Error, "Conform failed. Target params must contain vertices and vertex indices");
    241: 				return false;	
    242: 			}
    243: 		}
    244: 
    245: 		if (InConformTargetMesh.TargetPartsType != ETargetPartsType::HeadOnly)
    246: 		{
    247: 			if (InConformTargetMesh.BodyVertices.IsEmpty() || InConformTargetMesh.BodyVertexIndices.IsEmpty())
    248: 			{
    249: 				UE_LOGF(LogMetaHumanCoreTechLib, Error, "Conform failed. Target params must contain vertices and vertex indices");
    250: 				return false;	
    251: 			}
    252: 		}
    253: 
    254: 		return true;
    255: 	}
    256: 
    257: 	bool BuildSolveTarget(
    258: 		const FConformTargetParams& InConformTargetParams,
    259: 		std::shared_ptr<const TITAN_API_NAMESPACE::MetaHumanCreatorBodyAPI> InMHCBodyAPI,
    260: 		TITAN_NAMESPACE::BodyShapeEditorTarget& OutSolveTarget)
    261: 	{
    262: 		const FConformTargetMesh& TargetMesh = InConformTargetParams.ConformTargetMesh;
    263: 
    264: 		const TArray<FVector3f> HeadVerticesDNASpace = GetVerticesDNASpace(TargetMesh.HeadVertices);
    265: 		const TArray<FVector3f> BodyVerticesDNASpace = GetVerticesDNASpace(TargetMesh.BodyVertices);
    266: 
    267: 		const auto FaceLandmarks = GetFaceTrackingLandmarkData(InConformTargetParams.CurveTrackingPoints);
    268: 		const auto ViewportCamera = GetMetaShapeCamera(InConformTargetParams.CameraViewInfo, InConformTargetParams.ImageSize, "Front");
    269: 		const auto KeyPointCorrespondences = GetKeypointCorrespondences(InConformTargetParams.KeyPointTargets);
    270: 		auto LandmarkConstraints = InMHCBodyAPI->CreateLandmarkConstraints(FaceLandmarks, ViewportCamera);
    271: 
    272: 		bool bBuildOk = false;
    273: 		switch (TargetMesh.TargetPartsType)
    274: 		{
    275: 		case ETargetPartsType::HeadOnly:
    276: 			bBuildOk = TITAN_API_NAMESPACE::MetaHumanCreatorBodyAPI::BuildHeadOnlySolveTarget(
    277: 				GetEigenVertices(HeadVerticesDNASpace),
    278: 				GetEigenVertexIndices(TargetMesh.HeadVertexIndices),
    279: 				KeyPointCorrespondences, LandmarkConstraints,
    280: 				OutSolveTarget);
    281: 			break;
    282: 		case ETargetPartsType::BodyOnly:
    283: 			bBuildOk = TITAN_API_NAMESPACE::MetaHumanCreatorBodyAPI::BuildBodyOnlySolveTarget(
    284: 				GetEigenVertices(BodyVerticesDNASpace),
    285: 				GetEigenVertexIndices(TargetMesh.BodyVertexIndices),
    286: 				KeyPointCorrespondences, LandmarkConstraints,
    287: 				OutSolveTarget);
    288: 			break;
    289: 		case ETargetPartsType::HeadAndBody:
    290: 			{
    291: 				bBuildOk = TITAN_API_NAMESPACE::MetaHumanCreatorBodyAPI::BuildHeadAndBodySolveTarget(
    292: 					GetEigenVertices(HeadVerticesDNASpace),
    293: 					GetEigenVertexIndices(TargetMesh.HeadVertexIndices),
    294: 					GetEigenVertices(BodyVerticesDNASpace),
    295: 					GetEigenVertexIndices(TargetMesh.BodyVertexIndices),
    296: 					KeyPointCorrespondences, LandmarkConstraints,
    297: 					OutSolveTarget);
    298: 				break;
    299: 			}
    300: 		case ETargetPartsType::Combined:
    301: 		default:
    302: 			bBuildOk = TITAN_API_NAMESPACE::MetaHumanCreatorBodyAPI::BuildCombinedSolveTarget(
    303: 				GetEigenVertices(BodyVerticesDNASpace),
    304: 				GetEigenVertexIndices(TargetMesh.BodyVertexIndices),
    305: 				KeyPointCorrespondences, LandmarkConstraints,
    306: 				OutSolveTarget);
    307: 			break;
    308: 		}
    309: 
    310: 		if (!bBuildOk)
    311: 		{
    312: 			return false;
    313: 		}
    314: 
    315: 		TArray<float> JointRotationsView;
    316: 		if (TargetMesh.BodyJointRotations.Num() > 0)
    317: 		{
    318: 			JointRotationsView.SetNumUninitialized(TargetMesh.BodyJointRotations.Num() * 3);
    319: 			for (int32 i = 0; i < TargetMesh.BodyJointRotations.Num(); ++i)
    320: 			{
    321: 				JointRotationsView[i * 3 + 0] = TargetMesh.BodyJointRotations[i].X;
    322: 				JointRotationsView[i * 3 + 1] = -TargetMesh.BodyJointRotations[i].Y;
    323: 				JointRotationsView[i * 3 + 2] = -TargetMesh.BodyJointRotations[i].Z;
    324: 			}
    325: 		}

    442: bool FMetaHumanCharacterBodyIdentity::Init(const FString& InModelPath, const FString& InLegacyBodiesPath,  const TSharedPtr<FMetaHumanCharacterIdentity>& InFaceIdentity)
    443: {
    444: #if WITH_EDITORONLY_DATA
    445: 
    446: 	FString BodyPCAModelPath = InModelPath + TEXT("/body_model.dna");
    447: 	FString BodySkinModelPath = InModelPath + TEXT("/skin_model.binary");
    448: 	FString BodyRBFModelPath = InModelPath + TEXT("/rbf_model.binary");
    449: 	
    450: 	TArray<uint8> PCAModelBuffer;
    451: 	if (!FFileHelper::LoadFileToArray(PCAModelBuffer, *BodyPCAModelPath))
    452: 	{
    453: 		UE_LOGF(LogMetaHumanCoreTechLib, Error, "failed to load MHC body model");
    454: 		return false;
    455: 	}
    456: 	TSharedPtr<IDNAReader> PCAModelReader = ReadDNAFromBuffer(&PCAModelBuffer, EDNADataLayer::All);
    457: 	
    458: 	FString CombinedBodyArchetypeFilename = FMetaHumanCommonDataUtils::GetCombinedDNAFilesystemPath();
    459: 	TArray<uint8> CombinedDNABuffer;
    460: 	if (!FFileHelper::LoadFileToArray(CombinedDNABuffer, *CombinedBodyArchetypeFilename))
    461: 	{
    462: 		UE_LOGF(LogMetaHumanCoreTechLib, Error, "failed to load MHC body model");
    463: 		return false;
    464: 	}
    465: 	TSharedPtr<IDNAReader> CombinedBodyArchetypeReader = ReadDNAFromBuffer(&CombinedDNABuffer, EDNADataLayer::All);
    466: 
    467: 	FString PhysicsBodiesConfigPath = InModelPath + TEXT("/physics_bodies.json");
    468: 	FString PhysicsBodiesMaskPath = InModelPath + TEXT("/bodies_mask.json");
    469: 	FString SkinningWeightGenerationConfigPath = InModelPath + TEXT("/body_joint_mapping.json");
    470: 	FString LodGenerationDataPath = InModelPath + TEXT("/combined_lod_generation.binary");
    471: 	FString RegionsLandmarksPath = InModelPath + TEXT("/region_landmarks.json");
    472: 	FString SolvePipelinesPath = InModelPath + TEXT("/pipeline_presets.json");
    473: 
    474: 	std::shared_ptr<TITAN_NAMESPACE::PatchBlendModel<float>> FacePatchBlendModel = nullptr;
    475: 	std::shared_ptr<TITAN_NAMESPACE::MeshLandmarks<float>> FaceTrackingLandmarks = nullptr;
    476: 	if (InFaceIdentity)
    477: 	{
    478: 		if (const TITAN_API_NAMESPACE::MetaHumanCreatorAPI* MHCAPI = InFaceIdentity->GetMHCAPIPtr())
    479: 		{
    480: 			FacePatchBlendModel = MHCAPI->GetFacePatchBlendModel();
    481: 			FaceTrackingLandmarks = MHCAPI->GetFaceTrackingLandmarks();
    482: 		}
    483: 	}
    484: 
    485: 	std::shared_ptr<TITAN_API_NAMESPACE::MetaHumanCreatorBodyAPI> MHCBodyAPI = TITAN_API_NAMESPACE::MetaHumanCreatorBodyAPI::CreateMHCBodyApi(
    486: 		PCAModelReader->Unwrap(), 
    487: 		CombinedBodyArchetypeReader->Unwrap(),
    488: 		TCHAR_TO_UTF8(*BodyRBFModelPath),
    489: 		TCHAR_TO_UTF8(*BodySkinModelPath),
    490: 		TCHAR_TO_UTF8(*SkinningWeightGenerationConfigPath),
    491: 		TCHAR_TO_UTF8(*LodGenerationDataPath),

    592: TArray<FMetaHumanCharacterBodyConstraint> FMetaHumanCharacterBodyIdentity::FState::GetBodyConstraints(bool bScaleMeasurementRangesWithHeight) const
    593: {
    594: 	check(Impl->MHCBodyAPI);
    595: 	check(Impl->MHCBodyState);
    596: 
    597: 	TArray<FMetaHumanCharacterBodyConstraint> BodyConstraints;
    598: 
    599: 	int ConstraintsNum = Impl->MHCBodyState->GetConstraintNum();
    600: 	BodyConstraints.AddUninitialized( StaticCast<int32>(ConstraintsNum));
    601: 	av::ConstArrayView<float> Measurements =  Impl->MHCBodyState->GetMeasurements();
    602: 
    603: 	std::vector<float> MinValues;
    604: 	std::vector<float> MaxValues;
    605: 	MinValues.resize(ConstraintsNum);
    606: 	MaxValues.resize(ConstraintsNum);
    607: 	Impl->MHCBodyAPI->EvaluateConstraintRange(*(Impl->MHCBodyState), MinValues, MaxValues, bScaleMeasurementRangesWithHeight);
    608: 
    609: 	for (int ConstraintIndex = 0; ConstraintIndex < ConstraintsNum; ConstraintIndex++)
    610: 	{
    611: 		FMetaHumanCharacterBodyConstraint BodyConstraint;
    612: 		std::string StdConstraintName(Impl->MHCBodyState->GetConstraintName(ConstraintIndex));
    613: 		BodyConstraint.Name = UTF8_TO_TCHAR(StdConstraintName.c_str());
    614: 
    615: 		float TargetMeasurement = 0.f;
    616: 		bool bIsActive = Impl->MHCBodyState->GetConstraintTarget(ConstraintIndex, TargetMeasurement);
    617: 		BodyConstraint.bIsActive = bIsActive;
    618: 
    619: 		if (bIsActive)
    620: 		{
    621: 			BodyConstraint.TargetMeasurement = TargetMeasurement;
    622: 		}
    623: 		else
    624: 		{
    625: 			BodyConstraint.TargetMeasurement = Measurements[ConstraintIndex];
    626: 		}
    627: 
    628: 		BodyConstraint.MinMeasurement = MinValues[ConstraintIndex];
    629: 		BodyConstraint.MaxMeasurement = MaxValues[ConstraintIndex];
    630: 		BodyConstraints[ConstraintIndex] = BodyConstraint;
    631: 	}
    632: 
    633: 	return BodyConstraints;
    634: }
    635: 
    636: void FMetaHumanCharacterBodyIdentity::FState::EvaluateBodyConstraints(const TArray<FMetaHumanCharacterBodyConstraint>& BodyConstraints)
    637: {
    638: 	check(Impl->MHCBodyAPI);
    639: 	check(Impl->MHCBodyState);
    640: 
    641: 	TArray<FVector3f> Out;
    642: 
    643: 	std::shared_ptr<TITAN_API_NAMESPACE::MetaHumanCreatorBodyAPI::State> NewBodyShapeState;
    644: 	NewBodyShapeState = Impl->MHCBodyState->Clone();
    645: 
    646: 	for (int32 ConstraintIndex = 0; ConstraintIndex < BodyConstraints.Num(); ConstraintIndex++)
    647: 	{
    648: 		if (BodyConstraints[ConstraintIndex].bIsActive)
    649: 		{
    650: 			NewBodyShapeState->SetConstraintTarget(StaticCast<int>(ConstraintIndex), BodyConstraints[ConstraintIndex].TargetMeasurement);
    651: 		}
    652: 		else
    653: 		{
    654: 			NewBodyShapeState->RemoveConstraintTarget(StaticCast<int>(ConstraintIndex));

    1333: bool FMetaHumanCharacterBodyIdentity::FState::ConformTarget(const FConformTargetParams& InConformTargetParams)
    1334: {
    1335: 	if (!UE::MetaHuman::ValidateConformTargetMesh(InConformTargetParams.ConformTargetMesh))
    1336: 	{
    1337: 		return false;
    1338: 	}
    1339: 
    1340: 	// Build a solve target using the appropriate function for the target parts type
    1341: 	TITAN_NAMESPACE::BodyShapeEditorTarget SolveTarget;
    1342: 	Eigen::VectorXf TargetVertexWeights;
    1343: 	if (!UE::MetaHuman::BuildSolveTarget(InConformTargetParams, Impl->MHCBodyAPI, SolveTarget))
    1344: 	{
    1345: 		return false;
    1346: 	}
    1347: 
    1348: 	const FConformTargetMesh& TargetMesh = InConformTargetParams.ConformTargetMesh;
    1349: 
    1350: 	const FBodyConformSolveSettings& SolveSettings = InConformTargetParams.BodyConformSolveSettings;
    1351: 	TITAN_API_NAMESPACE::MetaHumanCreatorBodyAPI::ArbitraryFitSolveOptions SolveOptions = UE::MetaHuman::GetFitSolveOptions(SolveSettings);
    1352: 
    1353: 	std::shared_ptr<TITAN_API_NAMESPACE::MetaHumanCreatorBodyAPI::State> NewBodyState = Impl->MHCBodyState->Clone();
    1354: 	NewBodyState->SetApplyFloorOffset(false);
    1355: 	Impl->MHCBodyAPI->ClearVertexDeltas(*NewBodyState);
    1356: 
    1357: 	auto IterationUpdate = [this] (const av::ConstArrayView<float> InVerticesArray, const av::ConstArrayView<float> InNormalsArray, const av::ConstArrayView<float> InBindPose, int InIterationCount, TITAN_API_NAMESPACE::MetaHumanCreatorBodyAPI::ESolveStepType InSolveStepType)
    1358: 	{
    1359: 		FMetaHumanRigEvaluatedState IterationState;
    1360: 
    1361: 		IterationState.Vertices.AddUninitialized(InVerticesArray.size() / 3);
    1362: 		float* VerticesDataPtr = (float*)(IterationState.Vertices.GetData());
    1363: 		FMemory::Memcpy(VerticesDataPtr, InVerticesArray.data(), InVerticesArray.size() * sizeof(float));
    1364: 
    1365: 		IterationState.VertexNormals.AddUninitialized(InNormalsArray.size() / 3);
    1366: 		float* NormalsDataPtr = (float*)(IterationState.VertexNormals.GetData());
    1367: 		FMemory::Memcpy(NormalsDataPtr, InNormalsArray.data(), InNormalsArray.size() * sizeof(float));
    1368: 
    1369: 		TArray<FMatrix44f> BindPoseMatrices;
    1370: 		BindPoseMatrices.AddUninitialized(InBindPose.size() / 16);
    1371: 		FMemory::Memcpy((float*)BindPoseMatrices.GetData(), InBindPose.data(), InBindPose.size()*sizeof(float));
    1372: 
    1373: 		return !Impl->MeshConformIterationDelegate.IsBound() || Impl->MeshConformIterationDelegate.Execute(IterationState, BindPoseMatrices, InIterationCount, static_cast<ESolveStepType>(InSolveStepType));
    1374: 	};
    1375: 	
    1376: 	if (InConformTargetParams.bAutoSolve)
    1377: 	{
    1378: 		std::string PipelineName = TCHAR_TO_UTF8(*SolveSettings.PipelineName);	
    1379: 		if (!Impl->MHCBodyAPI->PipelineFitToArbitraryTarget(*NewBodyState, PipelineName, SolveOptions, SolveTarget,IterationUpdate))
    1380: 		{
    1381: 			return false;
    1382: 		}
    1383: 	}
    1384: 	else
    1385: 	{
    1386: 		// if doing body solve step
    1387: 		if (SolveSettings.Iterations > 0)
    1388: 		{
    1389: 			if (!Impl->MHCBodyAPI->FitToArbitraryTarget(*NewBodyState, SolveOptions, SolveTarget,IterationUpdate))
    1390: 			{
    1391: 				return false;
    1392: 			}
    1393: 
    1394: 			if (SolveSettings.bApplyNeckSeamSmoothing)
    1395: 			{
    1396: 				TITAN_API_NAMESPACE::MetaHumanCreatorBodyAPI::AdaptNeckSeamParams NeckSeamParams;
    1397: 				NeckSeamParams.iterations = SolveSettings.SeamIterations;
    1398: 				NeckSeamParams.laplacianWeight = SolveSettings.SeamLaplacian;
    1399: 				NeckSeamParams.rings = SolveSettings.SeamRings;
    1400: 				if (!Impl->MHCBodyAPI->AdaptNeckSeam(*NewBodyState, NeckSeamParams))
    1401: 				{
    1402: 					return false;
    1403: 				}
    1404: 			}
    1405: 		}
    1406: 		
    1407: 		// if doing face solve step
    1408: 		if (SolveSettings.FaceIterations > 0 && TargetMesh.TargetPartsType != ETargetPartsType::BodyOnly)
    1409: 		{
    1410: 			if (!Impl->MHCBodyAPI->FitFaceToArbitraryTarget(*NewBodyState, SolveOptions, SolveTarget,IterationUpdate))
    1411: 			{
    1412: 				return false;
    1413: 			}
    1414: 			
    1415: 			if (SolveSettings.bApplyNeckSeamSmoothing)
    1416: 			{
    1417: 				TITAN_API_NAMESPACE::MetaHumanCreatorBodyAPI::AdaptNeckSeamParams NeckSeamParams;
    1418: 				NeckSeamParams.iterations = SolveSettings.SeamIterations;
    1419: 				NeckSeamParams.laplacianWeight = SolveSettings.SeamLaplacian;
    1420: 				NeckSeamParams.rings = SolveSettings.SeamRings;
    1421: 				if (!Impl->MHCBodyAPI->AdaptNeckSeam(*NewBodyState, NeckSeamParams))
    1422: 				{
    1423: 					return false;
    1424: 				}
    1425: 			}
    1426: 		}
    1427: 	}
    1428: 
    1429: 	if (InConformTargetParams.bEstimateBodyJointsFromMesh)
    1430: 	{
    1431: 		Impl->MHCBodyAPI->VolumetricallyFitHandAndFeetJoints(*NewBodyState);
    1432: 	}
    1433: 	Impl->MHCBodyState = NewBodyState;
    1434: 	return true;
    1435: }
    1436: 

## S05

[MetaHumanCreatorBodyAPI.cpp](<D:/Epic Games/UE_5.8/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib/Source/MetaHumanCoreTechLib/Private/api/MetaHumanCreatorBodyAPI.cpp>): D:\Epic Games\UE_5.8\Engine\Plugins\MetaHuman\MetaHumanCoreTechLib\Source\MetaHumanCoreTechLib\Private\api\MetaHumanCreatorBodyAPI.cpp

    142: static bool BuildSolveTargetMesh(
    143: 									const Eigen::Ref<const Eigen::Matrix<float, 3, -1>> vertices,
    144: 									const Eigen::Ref<const Eigen::Matrix<int, 3, -1>> triangleIndices,
    145: 									std::shared_ptr<Mesh<float>>& outMesh)
    146: {
    147: 	const int numVertices = static_cast<int>(vertices.cols());
    148: 	const int numTriangles = static_cast<int>(triangleIndices.cols());
    149: 
    150: 	for (int i = 0; i < numTriangles; ++i)
    151: 	{
    152: 		for (int k = 0; k < 3; ++k)
    153: 		{
    154: 			const int vertexIndex = triangleIndices(k, i);
    155: 			if (vertexIndex < 0 || vertexIndex >= numVertices)
    156: 			{
    157: 				LOG_ERROR("Invalid triangle index: triangle {} vertex {} has index {} but vertex count is {}",
    158: 					i, k, vertexIndex, numVertices);
    159: 				return false;
    160: 			}
    161: 		}
    162: 	}
    163: 
    164: 	auto targetMesh = std::make_shared<Mesh<float>>();
    165: 	targetMesh->SetTriangles(triangleIndices);
    166: 	targetMesh->SetVertices(vertices);
    167: 	targetMesh->CalculateVertexNormals();
    168: 
    169: 	outMesh = targetMesh;
    170: 	return true;
    171: }
    172: 
    173: bool MetaHumanCreatorBodyAPI::BuildCombinedSolveTarget(const Eigen::Ref<const Eigen::Matrix<float, 3, -1>> vertices,
    174: 											const Eigen::Ref<const Eigen::Matrix<int, 3, -1>> triangleIndices,
    175: 											const std::vector<std::pair<int, Eigen::Vector3f>>& keyPointCorrespondences,
    176: 											const std::shared_ptr<LandmarkConstraints2D<float>>& landmarkConstraints2D,
    177: 											BodyShapeEditorTarget& outSolveTarget)
    178: {
    179: 	std::shared_ptr<Mesh<float>> mesh;
    180: 	if (!BuildSolveTargetMesh(vertices, triangleIndices, mesh))
    181: 		return false;
    182: 
    183: 	outSolveTarget.SetMesh(BodyShapeEditorTarget::MeshSlot::Combined, mesh);
    184: 	for (const auto& [vIdx, pos] : keyPointCorrespondences)
    185: 		outSolveTarget.AddKeypoint(vIdx, pos);
    186: 	outSolveTarget.SetLandmarks2D(landmarkConstraints2D);
    187: 	return true;
    188: }

    320:         JsonElement json = FMetaHumanFileResourceLoader::GetJsonElementForFile(CombinedSkinningWeightGenerationConfigPath);
    321:         CombinedBodyJointLodMapping<float> jointMapping;
    322:         bool bLoadMapping = jointMapping.ReadJson(json);
    323:         if (!bLoadMapping)
    324:         {
    325:             LOG_ERROR("Failed to parse skinning weight generation config for body model");
    326:             return nullptr;
    327:         }
    328: 
    329:         const std::vector<int> MaxSkinWeightsPerLod = { 12, 8, 8, 4 };
    330: 
    331:         auto skinModelMemoryStream = FMetaHumanFileResourceLoader::GetBoundedIOStreamFromFile(SkinModelPath);
    332:         auto RBFModelMemoryStream = FMetaHumanFileResourceLoader::GetBoundedIOStreamFromFile(RBFModelPath);
    333:         
    334:         skinModelMemoryStream->open();
    335:         RBFModelMemoryStream->open();
    336:         APIInstance->m->ptr.Init(PCABodyModel, RBFModelMemoryStream.get(), skinModelMemoryStream.get(), InCombinedBodyArchetypeDnaReader, jointMapping.GetJointMapping(), MaxSkinWeightsPerLod, CombinedLodGenerationData);
    337:         skinModelMemoryStream.release();

    1284: 
    1285: bool MetaHumanCreatorBodyAPI::FitToArbitraryTarget(State& state,
    1286:        const ArbitraryFitSolveOptions& options,
    1287:        const BodyShapeEditorTarget& solveTarget,
    1288:        IterationFunc iterationFunc) const
    1289: {
    1290: 	struct FCancelled {};
    1291:     try
    1292:     {
    1293:         TITAN_RESET_ERROR;
    1294:         auto newState = std::make_shared<BodyShapeEditor::State>(*state.m->ptr);
    1295:     
    1296:         auto iterationBodyCallback = [iterationFunc](const Eigen::Matrix<float, 3, -1>& vertices, const Eigen::Matrix<float, 3, -1>& normals, int iterationCount, float, const std::vector<Eigen::Transform<float, 3, Eigen::Affine>>& jointMatrices)
    1297:         {
    1298:             if (iterationFunc)
    1299:             {
    1300:                 av::ConstArrayView<float> bindPose((const float*)jointMatrices.data(), sizeof(Eigen::Transform<float, 3, Eigen::Affine>) / sizeof(float) *jointMatrices.size());
    1301:                 if (!iterationFunc(vertices, normals, bindPose, iterationCount, ESolveStepType::BodySolve))
    1302:                 {
    1303:                 	throw FCancelled{};
    1304:                 }
    1305:             }
    1306:         };
    1307: 
    1308: 	    BodySolveConfiguration bseSolveConfiguration = options.bodySolveConfiguration;
    1309: 
    1310:         if (!options.bSolveForPose)
    1311:         {
    1312:             const auto& cn = m->ptr.GetGuiControlNames();
    1313:             std::vector<int> pi;
    1314:             for (int i = 0; i < static_cast<int>(cn.size()); ++i)
    1315:                 if (cn[i].find("pose_driver") == 0) pi.push_back(i);
    1316:             // Locks must go on newState (the solver's working copy) — writing them
    1317:             // to state.m->ptr is a no-op against the solve because the solver never
    1318:             // reads the caller's state. bSolveForPose=false was silently broken here.
    1319:             auto ex = newState->GetLockedControlIndices();
    1320:             ex.insert(ex.end(), pi.begin(), pi.end());
    1321:             newState->SetLockedControlIndices(ex);
    1322:         }
    1323: 
    1324:     	if (options.bReloadSolveConfigurations)
    1325:     	{
    1326:     		// Shared PipelineBundle loader — reads the JSON config + its companion
    1327:     		// <name>.masks.bin sidecar (if present), ingests BSE part weights so any
    1328:     		// step.maskNames that reference "body" / "head" / etc. resolve. Populates
    1329:     		// the legacy m->pipelines / m->controlGroups / m->maskPresets maps so
    1330:     		// the downstream name-resolution loop below needs no changes.
    1331:     		PipelineBundle bundle;
    1332:     		if (!LoadPipelineBundle(m->pipelinePresetsJsonFilepath, &m->ptr, bundle))
    1333:     		{
    1334:     			LOG_ERROR("Failed to parse pipeline bundle '{}' for body solve", m->pipelinePresetsJsonFilepath);
    1335:     			return false;
    1336:     		}
    1337:     		m->pipelines     = std::move(bundle.pipelines);
    1338:     		m->controlGroups = std::move(bundle.controlGroups);
    1339:     		m->maskPresets   = std::move(bundle.masks);
    1340:     	}
    1341: 
    1342: 		m->ptr.SolveForArbitraryMeshWithICP(*newState,
    1343: 			solveTarget,
    1344: 			bseSolveConfiguration,
    1345: 			{},
    1346: 			iterationBodyCallback);
    1347:     
    1348: 		for (int constraintIndex = 0; constraintIndex < newState->GetConstraintNum(); constraintIndex++)
    1349: 		{
    1350: 			newState->RemoveConstraintTarget(constraintIndex);
    1351: 		}
    1352: 
    1353:         newState->ClearLockedControls();
    1354:         state.m->ptr = newState;

    1568:     	std::vector<SolveStep> pipelineToRun;    	
    1569:     	if (m->pipelines.contains(pipelineName))
    1570:     	{
    1571:     		pipelineToRun = m->pipelines[pipelineName];
    1572:     	}
    1573:     	else
    1574:     	{
    1575:     		LOG_ERROR("Failed to find pipeline {}", pipelineName);
    1576:     		return false;
    1577:     	}
    1578: 
    1579:     	// Resolve per-step config + masks + locked controls before handoff. The BSE

## S06

[BodyShapeEditor.cpp](<D:/Epic Games/UE_5.8/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib/Source/MetaHumanCoreTechLib/Private/bodyshapeeditor/src/BodyShapeEditor.cpp>): D:\Epic Games\UE_5.8\Engine\Plugins\MetaHuman\MetaHumanCoreTechLib\Source\MetaHumanCoreTechLib\Private\bodyshapeeditor\src\BodyShapeEditor.cpp

    2603: bool BodyShapeEditor::SetTargetScaleAndRigidSolve(State& state, const Eigen::Matrix<float, 3, -1>& targetVertices, const BodySolveConfiguration& options)
    2604: {
    2605:     if (targetVertices.cols() == 0)
    2606:     {
    2607:         return false;
    2608:     }
    2609: 
    2610:     Mesh<float> meanMesh = m->rigGeometry->GetMesh(0); // Get mean model
    2611: 
    2612:     // Compute bounding box of masked region (or full mesh if no mask)
    2613:     Eigen::Vector3f meanMinCorner = Eigen::Vector3f::Constant(std::numeric_limits<float>::max());
    2614:     Eigen::Vector3f meanMaxCorner = Eigen::Vector3f::Constant(-std::numeric_limits<float>::max());
    2615: 
    2616:     if (options.vertexMask.size() > 0)
    2617:     {
    2618:         bool hasActiveVertices = false;
    2619:         for (int i = 0; i < meanMesh.NumVertices() && i < options.vertexMask.size(); ++i)
    2620:         {
    2621:             if (options.vertexMask[i] > 0.0f)
    2622:             {
    2623:                 meanMinCorner = meanMinCorner.cwiseMin(meanMesh.Vertices().col(i));
    2624:                 meanMaxCorner = meanMaxCorner.cwiseMax(meanMesh.Vertices().col(i));
    2625:                 hasActiveVertices = true;
    2626:             }
    2627:         }
    2628: 
    2629:         // If mask contains no active vertices, fall back to full mesh bounds
    2630:         if (!hasActiveVertices)
    2631:         {
    2632:             meanMinCorner = meanMesh.Vertices().rowwise().minCoeff();
    2633:             meanMaxCorner = meanMesh.Vertices().rowwise().maxCoeff();
    2634:         }
    2635:     }
    2636:     else
    2637:     {
    2638:         meanMinCorner = meanMesh.Vertices().rowwise().minCoeff();
    2639:         meanMaxCorner = meanMesh.Vertices().rowwise().maxCoeff();
    2640:     }
    2641: 
    2642:     // Compute target mesh bounding box
    2643:     Eigen::Vector3f targetMinCorner = targetVertices.rowwise().minCoeff();
    2644:     Eigen::Vector3f targetMaxCorner = targetVertices.rowwise().maxCoeff();
    2645: 
    2646:     float uniformScale = 1.0f;
    2647: 
    2648:     if (std::abs(meanMaxCorner.y() - meanMinCorner.y()) < scaleTolerence ||
    2649:         std::abs(targetMaxCorner.y() - targetMinCorner.y()) < scaleTolerence)
    2650:     {
    2651:         return false;
    2652:     }
    2653:     float meanHeight = meanMaxCorner.y() - meanMinCorner.y();
    2654:     float targetHeight = targetMaxCorner.y() - targetMinCorner.y();
    2655:     uniformScale = targetHeight / meanHeight;
    2656: 
    2657:     state.m->ScaleFactor = uniformScale;
    2658: 
    2659: 
    2660:     // Compute bbox centers
    2661:     Eigen::Vector3f meanBBoxCenter = (meanMinCorner + meanMaxCorner) * 0.5f * uniformScale;

    5241: void BodyShapeEditor::Private::SetMinMaxMeasurements(const State& State)
    5242: {
    5243: 	minMeasurementInput.resize(Constraints.size());
    5244: 	maxMeasurementInput.resize(Constraints.size());
    5245: 	variableMinMeasurementInput.resize(Constraints.size());
    5246: 	variableMaxMeasurementInput.resize(Constraints.size());
    5247: 
    5248: 	std::vector<int> missingIndices {};
    5249: 	for (int i = 0; i < Constraints.size(); i++)
    5250: 	{
    5251: 		minMeasurementInput[i] = Constraints[i].GetFixedMinInput();
    5252: 		maxMeasurementInput[i] = Constraints[i].GetFixedMaxInput();
    5253: 		variableMinMeasurementInput[i] = Constraints[i].GetVariableMinInput();
    5254: 		variableMaxMeasurementInput[i] = Constraints[i].GetVariableMaxInput();
    5255: 
    5256: 		bool fixedMeasurementsSet = minMeasurementInput[i] != BodyMeasurement::InvalidValue &&
    5257: 			maxMeasurementInput[i] != BodyMeasurement::InvalidValue;
    5258: 		
    5259: 		bool variableMeasurementsSet = variableMinMeasurementInput[i].first != BodyMeasurement::InvalidValue &&
    5260: 			variableMinMeasurementInput[i].second != BodyMeasurement::InvalidValue &&
    5261: 			variableMaxMeasurementInput[i].first != BodyMeasurement::InvalidValue &&
    5262: 			variableMaxMeasurementInput[i].second != BodyMeasurement::InvalidValue;

    5328: void BodyShapeEditor::Private::ScaleMinMaxMeasurements(const State& State)
    5329: {
    5330:     const float scaleFactor = State.m->ScaleFactor;
    5331:     
    5332:     std::vector<bool> applyScaleFactorToMeasurementInput;
    5333:     applyScaleFactorToMeasurementInput.reserve(State.m->Constraints.size());
    5334:     for (int i = 0; i < Constraints.size(); i++)
    5335:     {
    5336:         bool shouldApplyScale = Constraints[i].GetType() != BodyMeasurement::Semantic;
    5337:         applyScaleFactorToMeasurementInput.push_back(shouldApplyScale);
    5338:     }
    5339: 
    5340:     // Scale all min/max measurement inputs by the scale factor
    5341:     for (size_t i = 0; i < minMeasurementInput.size(); ++i)
    5342:     {
    5343:         if (applyScaleFactorToMeasurementInput[i])
    5344:         {
    5345:             minMeasurementInput[i] *= scaleFactor;
    5346:             maxMeasurementInput[i] *= scaleFactor;    
    5347:         }
    5348:     }
    5349: 
    5350:     // Scale variable min/max measurement inputs (both elements of the pair)
    5351:     for (size_t i = 0; i < variableMinMeasurementInput.size(); ++i)
    5352:     {
    5353:         if (applyScaleFactorToMeasurementInput[i])
    5354:         {
    5355:             variableMinMeasurementInput[i].first *= scaleFactor;
    5356:             variableMinMeasurementInput[i].second *= scaleFactor;
    5357:             variableMaxMeasurementInput[i].first *= scaleFactor;
    5358:             variableMaxMeasurementInput[i].second *= scaleFactor;
    5359:         }
    5360:     }
    5361: }
    5362: 
    5363: void BodyShapeEditor::EvaluateConstraintRange(const State& State, av::ArrayView<float> MinValues, av::ArrayView<float> MaxValues, bool bScaleWithHeight) const
    5364: {
    5365: 	const auto& constraints = State.m->Constraints;
    5366: 	if ((MinValues.size() != MaxValues.size()) || (MinValues.size() != constraints.size()))
    5367: 	{
    5368: 		CARBON_CRITICAL("Output values buffer is not of right size");
    5369: 	}
    5370: 	
    5371: 	m->SetMinMaxMeasurements(State);
    5372: 	m->ScaleMinMaxMeasurements(State);
    5373: 
    5374: 	if (bScaleWithHeight)
    5375: 	{
    5376: 		if (m->heightConstraintIndex < 0)
    5377: 		{
    5378: 			for (int i = 0; i < constraints.size(); i++)
    5379: 			{
    5380: 				const BodyMeasurement& constraint = constraints[i];
    5381: 				if (constraint.GetName() == "Height" || constraint.GetName() == "height")
    5382: 				{
    5383: 					m->heightConstraintIndex = i;
    5384: 					break;
    5385: 				}
    5386: 			}
    5387: 		}
    5388: 
    5389: 		if (m->heightConstraintIndex < 0 || m->heightConstraintIndex >= constraints.size())
    5390: 		{
    5391: 			CARBON_CRITICAL("Constraints must include a valid Height constraint");
    5392: 		}
    5393: 
    5394: 		// Get height constraint range and height measurement. Calculate height ratio to lerp ranges with.
    5395: 		const auto& measurements = State.GetNamedConstraintMeasurements();
    5396: 
    5397:         float height = 177.5f;
    5398:         // Get height from constraint target if available, otherwise from measurement 
    5399:         if (!State.GetConstraintTarget(m->heightConstraintIndex, height)) 
    5400:         {
    5401:             height = measurements[m->heightConstraintIndex];
    5402:         }
    5403: 		
    5404: 		float min = m->variableMinMeasurementInput[m->heightConstraintIndex].first;
    5405: 		float max = m->variableMaxMeasurementInput[m->heightConstraintIndex].second;
    5406: 		if (max <= min)
    5407: 		{
    5408: 			CARBON_CRITICAL("Height constraint invalid. Max is less than or equal to Min ");
    5409: 		}
    5410: 		float heightRatio = (height - min) / (max - min);
    5411: 		heightRatio = std::clamp(heightRatio, 0.f, 1.f);
    5412: 
    5413: 		for (int i = 0; i < m->variableMinMeasurementInput.size(); ++i)
    5414: 		{
    5415: 			MinValues[i] = std::lerp(m->variableMinMeasurementInput[i].first, m->variableMinMeasurementInput[i].second, heightRatio);
    5416: 			MaxValues[i] = std::lerp(m->variableMaxMeasurementInput[i].first, m->variableMaxMeasurementInput[i].second, heightRatio);
    5417: 		}
    5418: 	}
    5419: 	else

## S07

[MetaHumanConformTargetParams.h](<D:/Epic Games/UE_5.8/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib/Source/MetaHumanCoreTechLib/Public/MetaHumanConformTargetParams.h>): D:\Epic Games\UE_5.8\Engine\Plugins\MetaHuman\MetaHumanCoreTechLib\Source\MetaHumanCoreTechLib\Public\MetaHumanConformTargetParams.h

    1: // Copyright Epic Games, Inc. All Rights Reserved.
    2: 
    3: #pragma once
    4: 
    5: #include "CoreMinimal.h"
    6: #include "Containers/Array.h"        
    7: #include "Containers/Map.h"        
    8: #include "Math/Vector.h"          
    9: #include "MetaHumanConformSolverSettings.h"
    10: #include "Camera/CameraTypes.h"
    11: 
    12: #include "MetaHumanConformTargetParams.generated.h"
    13: 
    14: UENUM(BlueprintType)
    15: enum class ETargetPartsType : uint8
    16: {
    17: 	Combined,
    18: 	BodyOnly,
    19: 	HeadOnly,
    20: 	HeadAndBody
    21: };
    22: 
    23: USTRUCT(BlueprintType)
    24: struct FTrackingPoints
    25: {
    26: 	GENERATED_BODY()
    27: 
    28: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Conform")
    29: 	TArray<FVector2D> TrackingPoints;
    30: };
    31: 
    32: USTRUCT(BlueprintType)
    33: struct FConformTargetMesh
    34: {
    35: 	GENERATED_BODY();
    36: 	
    37: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Conform")
    38: 	ETargetPartsType TargetPartsType = ETargetPartsType::Combined;
    39: 
    40: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Conform")
    41: 	TArray<FVector3f> BodyVertices;
    42: 
    43: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Conform")
    44: 	TArray<int32> BodyVertexIndices;
    45: 
    46: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Conform")
    47: 	TArray<FVector3f> BodyJointRotations;
    48: 
    49: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Conform")
    50: 	TArray<FVector3f> HeadVertices;
    51: 	
    52: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Conform")
    53: 	TArray<int32> HeadVertexIndices;
    54: };
    55: 
    56: /**
    57: * Struct to contain parameters used to conform to a target
    58: */
    59: USTRUCT(BlueprintType)
    60: struct FConformTargetParams
    61: {
    62: 	GENERATED_BODY();
    63: 
    64: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Conform")
    65: 	FConformTargetMesh ConformTargetMesh;
    66: 
    67: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Conform")
    68: 	TMap<int32, FVector3f> KeyPointTargets;
    69: 
    70: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Conform")
    71: 	TMap<FString, FTrackingPoints> CurveTrackingPoints;
    72: 
    73: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Conform")
    74: 	FMinimalViewInfo CameraViewInfo;
    75: 
    76: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Conform")
    77: 	FIntPoint ImageSize = FIntPoint::ZeroValue;
    78: 
    79: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Conform")
    80: 	bool bEstimateBodyJointsFromMesh = false;
    81: 	
    82: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Conform")
    83: 	bool bAutoSolve = false;
    84: 
    85: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Conform")
    86: 	FBodyConformSolveSettings BodyConformSolveSettings;
    87: };
    88: 
    89: 
    90: USTRUCT(BlueprintType)
    91: struct FRefinementTargetParams
    92: {
    93: 	GENERATED_BODY();
    94: 
    95: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Conform")
    96: 	FConformTargetMesh ConformTargetMesh;
    97: 
    98: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Conform")
    99: 	TMap<int32, FVector3f> KeyPointTargets;
    100: 	
    101: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Conform")
    102: 	TMap<FString, FTrackingPoints> CurveTrackingPoints;
    103: 	
    104: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Conform")
    105: 	FMinimalViewInfo CameraViewInfo;
    106: 	
    107: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Conform")

## S08

[MetaHumanConformSolverSettings.h](<D:/Epic Games/UE_5.8/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib/Source/MetaHumanCoreTechLib/Public/MetaHumanConformSolverSettings.h>): D:\Epic Games\UE_5.8\Engine\Plugins\MetaHuman\MetaHumanCoreTechLib\Source\MetaHumanCoreTechLib\Public\MetaHumanConformSolverSettings.h

    35: struct FBodyConformSolveSettings
    36: {
    37: 	GENERATED_BODY();
    38: 	
    39: 	/* Name of the solver pipeline to use. */
    40: 	UPROPERTY(BlueprintReadWrite, Category = "Pipeline Solve")
    41: 	FString PipelineName;
    42: 
    43: 	/* Whether to solve for body pose. */
    44: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Body Solve")
    45: 	bool bSolvePose = true;
    46: 
    47: 	/* Enforces left - right body symmetry during fitting. */
    48: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Body Solve")
    49: 	bool bSymmetricalSolve = false;
    50: 	
    51: 	/* Number of fitting passes. More = finer result but slower. */
    52: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Body Solve", meta = (ClampMin = "0", UIMax = "100"))
    53: 	int Iterations = 13;
    54: 
    55: 	/* How strongly the surface tries to match the scan. Higher = tighter fit to scan geometry. */
    56: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Body Solve")
    57: 	FWeightSchedule IcpGeometryWeight = { 70.0f, 70.0f, EWeightScheduleCurve::Static };
    58: 
    59: 	/* Maximum distance (mm) to consider a scan point as a match. Ramps down each iteration for progressively tighter matching. */
    60: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Body Solve")
    61: 	FWeightSchedule IcpSearchTolerance = { 50.0f, 50.0f, EWeightScheduleCurve::Static };
    62: 
    63: 	/* Rejects scan points whose surface normal disagrees with the model normal. Lower = more permissive matching. */
    64: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Body Solve")
    65: 	FWeightSchedule IcpNormalCompatibility = { 0.8f, 0.8f, EWeightScheduleCurve::Static };
    66: 
    67: 	/* How strongly detected body keypoints (shoulders, hips, etc.) pull the rig into pose. */
    68: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Body Solve")
    69: 	FWeightSchedule IcpKeyPointWeight = { 1.0f, 1.0f, EWeightScheduleCurve::Static };
    70: 
    71: 	/* How strongly 2D landmark positions guide the fit. */
    72: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Body Solve")
    73: 	FWeightSchedule IcpLandmarksWeight = { 0.557f, 0.0f, EWeightScheduleCurve::Linear };
    74: 
    75: 	/* Resistance to overall shape change. Higher = stays closer to the base model shape. */
    76: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Body Solve")
    77: 	FWeightSchedule RegularizationGlobalControls = { 0.682f, 0.682f, EWeightScheduleCurve::Static };
    78: 
    79: 	/* Resistance to local surface deformation. Higher = smoother surface. */
    80: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Body Solve")
    81: 	FWeightSchedule RegularizationLocalControls = { 1.0f, 1.0f, EWeightScheduleCurve::Static };
    82: 
    83: 	/* Resistance to changing body proportions. Higher = preserves original proportions. */
    84: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Body Solve")
    85: 	FWeightSchedule RegularizationProportions = { 1.0f, 1.0f, EWeightScheduleCurve::Static };
    86: 
    87: 	/* Resistance to changing joint angles. Higher = stays closer to detected pose. */
    88: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Body Solve")
    89: 	FWeightSchedule RegularizationPose = { 2.0f, 0.5f, EWeightScheduleCurve::Linear };
    90: 
    91: 	/* Number of points used to resample curve constraints. Higher = more accurate curve matching. */
    92: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Body Solve", meta = (ClampMin = "0", UIMax = "100"))
    93: 	int CurveResampling = 5;
    94: 
    95: 	/* Number of fitting passes for face solve. More = finer result but slower. */
    96: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Face Solve", meta = (ClampMin = "0", UIMax = "100"))
    97: 	int FaceIterations = 7;
    98: 	
    99: 	/* How strongly the face surface tries to match the scan. Higher = tighter fit to scan geometry. */
    100: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Face Solve")
    101: 	FWeightSchedule FaceIcpWeight = { 30.0f, 30.0f, EWeightScheduleCurve::Static };
    102: 
    103: 	/* Maximum distance (mm) to consider a scan point as a match for face solve. Ramps down each iteration for progressively tighter matching. */

## S09

[example_conform_from_custom_mesh.py](<D:/Epic Games/UE_5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter/Content/Python/examples/example_conform_from_custom_mesh.py>): D:\Epic Games\UE_5.8\Engine\Plugins\MetaHuman\MetaHumanCharacter\Content\Python\examples\example_conform_from_custom_mesh.py

    1: """End-to-end conform of a MetaHumanCharacter to a custom static or skeletal
    2: mesh, using face landmark tracking on a pre-rendered portrait to drive the
    3: 2D landmark term of the solve.
    4: 
    5: Pipeline:
    6:     1. Load the portrait image into a TArray<FColor>.
    7:     2. Run TrackFaceLandmarksFromImage to get 2D facial contour curves.
    8:     3. Load the target mesh and extract topology (verts + tri indices) via
    9:        GetMeshDataForConforming.
    10:     4. Create a fresh MetaHumanCharacter asset.
    11:     5. Build FConformTargetParams: body mesh data + curve tracking + camera info.
    12:     6. Run ConformToTargetMeshes synchronously to fit body + face state.
    13:     7. Export the conformed posed DNA (combined head+body) for downstream tools.
    14:     8. Commit the posed state as the A pose so the saved asset is canonical.
    15:     9. Save the character asset.
    16: 
    17: The portrait must be pre-rendered (this example deliberately does NOT cover
    18: dynamic scene capture — that's a separate concern). The camera intrinsics
    19: below MUST match the camera that produced the image, since the 2D landmarks
    20: get back-projected into 3D during the solve.
    21: """
    22: import unreal
    23: 
    24: # Inputs ----------------------------------------------------------------------
    25: 
    26: # A pre-rendered front-facing portrait of TARGET_MESH on disk. PNG/JPEG accepted.
    27: PORTRAIT_IMAGE_PATH = r"D:\Path\To\Your\FacePortrait.png"
    28: 
    29: # The custom static or skeletal mesh to conform to.
    30: TARGET_MESH_PATH = "/Game/MyContent/MyTargetMesh"
    31: 

    90: if character is None:
    91:     raise RuntimeError(f"Failed to create character asset at {asset_path}")
    92: 
    93: if not metahuman_subsystem.try_add_object_to_edit(character):
    94:     # Roll back the just-created asset so we don't leave an orphan in the
    95:     # content browser if the editor lock is held elsewhere.
    96:     if not unreal.EditorAssetLibrary.delete_asset(asset_path):
    97:         unreal.log_warning(f"Failed to delete orphaned asset at {asset_path} — manual cleanup may be required")
    98:     raise RuntimeError("Unable to edit asset, is it already open for edit?")
    99: 
    100: # Track whether the conform finished successfully so we can roll back the
    101: # just-created asset if anything inside the `try` block raises or fails.
    102: conform_succeeded = False
    103: try:
    104:     # 5. Assemble conform params.
    105:     conform_params = unreal.ConformTargetParams()
    106:     conform_params.conform_target_mesh.target_parts_type = unreal.TargetPartsType.COMBINED
    107:     conform_params.conform_target_mesh.body_vertices = body_vertices
    108:     conform_params.conform_target_mesh.body_vertex_indices = body_indices
    109:     conform_params.estimate_body_joints_from_mesh = True
    110:     conform_params.auto_solve = True
    111:     conform_params.body_conform_solve_settings.pipeline_name = "combined"
    112: 
    113:     # 2D face tracking term — landmarks + the camera that produced them.
    114:     view_info = unreal.MinimalViewInfo()
    115:     view_info.location = CAMERA_LOCATION
    116:     view_info.rotation = CAMERA_ROTATION
    117:     view_info.fov = CAMERA_FOV_DEG
    118:     view_info.aspect_ratio = float(image_size.x) / float(image_size.y)
    119:     view_info.projection_mode = unreal.CameraProjectionMode.PERSPECTIVE
    120:     conform_params.curve_tracking_points = curve_tracking
    121:     conform_params.camera_view_info = view_info
    122:     conform_params.image_size = image_size
    123: 
    124:     # Optional A — per-vertex keypoint pin constraints for the SOLVER.
    125:     # FConformTargetParams.KeyPointTargets is the only place ConformToTargetMeshes
    126:     # reads keypoints from. Map: MH vertex index → target 3D position. Uncomment:
    127:     #
    128:     # conform_params.key_point_targets = {

    180: 
    181:     # Export the posed DNA BEFORE flipping the live state back to A pose — the
    182:     # export reads the conformed posed state stored under target_mesh_key and
    183:     # bakes it (combined head + body) into a single DNA asset. Downstream tools
    184:     # (material baking, etc.) consume this DNA.
    185:     posed_dna_export = unreal.MetaHumanPosedDNAExportParams()
    186:     posed_dna_export.target_mesh_key = target_mesh_key
    187:     # ProjectPath / ExternalPath are FOLDERS. AssetName is the asset/file name
    188:     # stem (without extension); falls back to "<CharacterName>_Posed" when empty.
    189:     # Set ExternalPath to also write a .dna file alongside the project asset.
    190:     posed_dna_export.project_path = OUTPUT_PACKAGE_PATH
    191:     # posed_dna_export.external_path = r"D:\Path\To\OutputFolder"
    192:     # posed_dna_export.asset_name = "MyCustomPosedDNA"
    193:     posed_dna_export.overwrite_existing_assets = True
    194:     unreal.MetaHumanCharacterExportBlueprintLibrary.export_posed_dna(character, posed_dna_export)
    195: 
    196:     # Re-evaluate the body in MetaHuman A pose and propagate to the face so the saved
    197:     # asset is in the canonical A pose for downstream consumers. The interactive Mesh
    198:     # Import tool does this on shutdown.
    199:     metahuman_subsystem.commit_posed_state_as_a_pose(character, target_mesh_key)
    200: 
    201:     unreal.EditorAssetLibrary.save_asset(asset_path, only_if_is_dirty=True)
    202:     unreal.log(f"Conform complete — saved {asset_path}")
    203:     conform_succeeded = True
    204: 
    205: finally:
    206:     if metahuman_subsystem.is_object_added_for_editing(character):
    207:         metahuman_subsystem.remove_object_to_edit(character)
    208:     if not conform_succeeded:
    209:         # Roll back the just-created asset so we don't leave an orphan or a
    210:         # partially-conformed character in the content browser on failure.
    211:         if not unreal.EditorAssetLibrary.delete_asset(asset_path):
    212:             unreal.log_warning(f"Failed to delete orphaned asset at {asset_path} — manual cleanup may be required")

## S10

[example_sculpt_body.py](<D:/Epic Games/UE_5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter/Content/Python/examples/example_sculpt_body.py>): D:\Epic Games\UE_5.8\Engine\Plugins\MetaHuman\MetaHumanCharacter\Content\Python\examples\example_sculpt_body.py

    1: import unreal
    2: 
    3: # Load the asset
    4: character = unreal.load_asset("/Game/Characters/MetaHumans/Jeff.Jeff")
    5: 
    6: # Get the MetaHuman Subsystem
    7: metahuman_subsystem = unreal.get_editor_subsystem(
    8:     unreal.MetaHumanCharacterEditorSubsystem
    9: )
    10: 
    11: # Try to edit the character
    12: if not metahuman_subsystem.try_add_object_to_edit(character):
    13:     raise RuntimeError("Unable to edit asset, is it already open for edit?")
    14: 
    15: try:
    16:     # Get a list of body constraints
    17:     body_constraints = metahuman_subsystem.get_body_constraints(character)
    18:     # Map each constraints name to the constraint so we can look up via name
    19:     # Names are identical to how they are presented in the UI, converting them to lowered
    20:     # strings and replacing spaces with _ for convenience.
    21:     body_constraints_map = {
    22:         str(constraint.name).lower().replace(" ", "_"): constraint
    23:         for constraint in body_constraints
    24:     }
    25: 
    26:     # Set the height constraint to be active, this will ensure that the parameteric system 
    27:     # will try to hit the target_measurement. With it set to False, target_measurement 
    28:     # will be ignored.
    29:     body_constraints_map["height"].is_active = True
    30:     body_constraints_map["height"].target_measurement = 190.0
    31: 
    32:     body_constraints_map["upper_arm_length"].is_active = True
    33:     body_constraints_map["upper_arm_length"].target_measurement = 38.5
    34: 
    35:     # Update the constraints in the subsystem. Known bug that it doesn't update the
    36:     # parametric UI if that is open at the same time.
    37:     metahuman_subsystem.set_body_constraints(character, list(body_constraints_map.values()))
    38:     metahuman_subsystem.commit_body_state(character)
    39: 
    40: finally:
    41:     # Finish Editing
    42:     if metahuman_subsystem.is_object_added_for_editing(character):
    43:         metahuman_subsystem.remove_object_to_edit(character)

## S11

[MetaHumanBodyType.h](<D:/Epic Games/UE_5.8/Engine/Plugins/MetaHuman/MetaHumanSDK/Source/MetaHumanSDKRuntime/Public/MetaHumanBodyType.h>): D:\Epic Games\UE_5.8\Engine\Plugins\MetaHuman\MetaHumanSDK\Source\MetaHumanSDKRuntime\Public\MetaHumanBodyType.h

    1: // Copyright Epic Games, Inc. All Rights Reserved.
    2: 
    3: #pragma once
    4: 
    5: #include "UObject/ObjectMacros.h"
    6: #include "Misc/EnumRange.h"
    7: #include "MetaHumanBodyType.generated.h"
    8: 
    9: UENUM()
    10: enum class EMetaHumanBodyType : uint8
    11: {
    12: 	f_med_nrw = 0,
    13: 	f_med_ovw,
    14: 	f_med_unw,
    15: 	f_srt_nrw,
    16: 	f_srt_ovw,
    17: 	f_srt_unw,
    18: 	f_tal_nrw,
    19: 	f_tal_ovw,
    20: 	f_tal_unw,
    21: 	m_med_nrw,
    22: 	m_med_ovw,
    23: 	m_med_unw,
    24: 	m_srt_nrw,
    25: 	m_srt_ovw,
    26: 	m_srt_unw,
    27: 	m_tal_nrw,
    28: 	m_tal_ovw,
    29: 	m_tal_unw,
    30: 	BlendableBody, // This is not required for CharacterBodyIdentity initialization. Keep it as last entry on enum list (before Count)
    31: 	Count UMETA(Hidden)
    32: };
    33: ENUM_RANGE_BY_COUNT(EMetaHumanBodyType, EMetaHumanBodyType::Count);
    34: 
    35: UENUM()
    36: enum class EMetaHumanBodyBodyPartIndex : uint32

## S12

[FbxAssetImportData.h](<D:/Epic Games/UE_5.8/Engine/Source/Editor/UnrealEd/Classes/Factories/FbxAssetImportData.h>): D:\Epic Games\UE_5.8\Engine\Source\Editor\UnrealEd\Classes\Factories\FbxAssetImportData.h

    1: // Copyright Epic Games, Inc. All Rights Reserved.
    2: 
    3: #pragma once
    4: 
    5: #include "CoreMinimal.h"
    6: #include "UObject/ObjectMacros.h"
    7: #include "EditorFramework/AssetImportData.h"
    8: #include "FbxAssetImportData.generated.h"
    9: 
    10: class UFbxSceneImportData;
    11: 
    12: UENUM(BlueprintType)
    13: enum class ECoordinateSystemPolicy : uint8
    14: {
    15: 	MatchUpForwardAxes UMETA(DisplayName = "Match Up and Forward Axes", Tooltip = "The Up and Front axes in the FBX are mapped to the Up and Forward axes in UEFN.\nAfter import, the model will have the same apparent orientation in UEFN as itn oes in the FBX"),
    16: 	MatchUpAxis UMETA(DisplayName = "Match Up Axis", Tooltip = "The Up axis in the FBX is mapped to the Up axis in UEFN.\nAfter import, the model will have the same apparent vertical axis in UEFN as it does in the FBX, but its Forward and Left orientations may not match the FBX."),
    17: 	KeepXYZAxes UMETA(DisplayName = "Keep XYZ Axes", Tooltip = "The X, Y, and Z axes in the FBX are mapped directly to UEFN's internal X, Y, and Z axes, only flipping the Y axis to change from right - handed to left - handed coordinates.\nThis applies the least change to the data, but is least likely to match UEFN's Left, Up, and Forward axis conventions."),
    18: };
    19: 
    20: 
    21: /**
    22:  * Base class for import data and options used when importing any asset from FBX
    23:  */
    24: UCLASS(BlueprintType, config=EditorPerProjectUserSettings, HideCategories=Object, abstract, MinimalAPI)
    25: class UFbxAssetImportData : public UAssetImportData
    26: {
    27: 	GENERATED_UCLASS_BODY()
    28: 
    29: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, config, Category=Transform, meta=(ImportType="StaticMesh|SkeletalMesh|Animation", ImportCategory="Transform"))
    30: 	FVector ImportTranslation;
    31: 
    32: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, config, Category=Transform, meta=(ImportType="StaticMesh|SkeletalMesh|Animation", ImportCategory="Transform"))
    33: 	FRotator ImportRotation;
    34: 
    35: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, config, Category=Transform, meta=(ImportType="StaticMesh|SkeletalMesh|Animation", ImportCategory="Transform"))
    36: 	float ImportUniformScale;
    37: 
    38: 	/** Whether to convert scene from FBX scene. */
    39: 	UPROPERTY(EditAnywhere, Transient, config, Category = Miscellaneous, meta = (EditCondition = "bUsingLUFCoordinateSysem", EditConditionHides,  ImportType = "StaticMesh|SkeletalMesh|Animation", ImportCategory = "Miscellaneous", ToolTip = "Select strategy to map FBX coordinates system to UE coordinates system"))
    40: 	ECoordinateSystemPolicy CoordinateSystemPolicy = ECoordinateSystemPolicy::MatchUpForwardAxes;
    41: 
    42: 	/** Whether to convert scene from FBX scene. */
    43: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, config, Category = Miscellaneous, meta = (EditCondition = "!bUsingLUFCoordinateSysem", EditConditionHides, ImportType = "StaticMesh|SkeletalMesh|Animation", ImportCategory = "Miscellaneous", ToolTip = "Convert the scene from FBX coordinate system to UE coordinate system"))
    44: 	bool bConvertScene;
    45: 
    46: 	/** Whether to force the front axis to be align with X instead of -Y. */
    47: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, config, Category = Miscellaneous, meta = (EditCondition = "bConvertScene && !bUsingLUFCoordinateSysem", EditConditionHides, ImportType = "StaticMesh|SkeletalMesh|Animation", ImportCategory = "Miscellaneous", ToolTip = "Convert the scene from FBX coordinate system to UE coordinate system with front X axis instead of -Y"))
    48: 	bool bForceFrontXAxis;
    49: 
    50: 	/** Whether to convert the scene from FBX unit to UE unit (centimeter). */
    51: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, config, Category = Miscellaneous, meta = (ImportType = "StaticMesh|SkeletalMesh|Animation", ImportCategory = "Miscellaneous", ToolTip = "Convert the scene from FBX unit to UE unit (centimeter)."))
    52: 	bool bConvertSceneUnit;
    53: 
    54: 	/* Use by the reimport factory to answer CanReimport, if true only factory for scene reimport will return true */
    55: 	UPROPERTY()
    56: 	bool bImportAsScene;
    57: 
    58: 	/* Use by the reimport factory to answer CanReimport, if true only factory for scene reimport will return true */
    59: 	UPROPERTY()
    60: 	TObjectPtr<UFbxSceneImportData> FbxSceneImportDataReference;
    61: 
    62: 	/* Use to enable or not the new UI */
    63: 	UPROPERTY(Transient, VisibleDefaultsOnly, config, Category = InternalOnly)
    64: 	bool bUsingLUFCoordinateSysem;
    65: 
    66: 	virtual void PostEditChangeProperty(struct FPropertyChangedEvent& PropertyChangedEvent) override;
    67: };

## S13

[InterchangeGenericAssetsPipeline.h](<D:/Epic Games/UE_5.8/Engine/Plugins/Interchange/Runtime/Source/Pipelines/Public/InterchangeGenericAssetsPipeline.h>): D:\Epic Games\UE_5.8\Engine\Plugins\Interchange\Runtime\Source\Pipelines\Public\InterchangeGenericAssetsPipeline.h

    63: 	/** Create an additional Content folder inside of the chosen import directory, and name it after the imported scene */
    64: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Common")
    65: 	bool bSceneNameSubFolder = false;
    66: 
    67: 	/** Group the assets according to their type into additional Content folders created on the import directory (/Materials, /StaticMeshes, /SkeletalMeshes, etc.) */
    68: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Common")
    69: 	bool bAssetTypeSubFolders = false;
    70: 
    71: 	/** If set, and there is only one asset and one source, the imported asset is given this name. */
    72: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Common", meta = (StandAlonePipelineProperty = "True"))
    73: 	FString AssetName;
    74: 
    75: 	/** Translation offset applied to meshes and animations. */
    76: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Common", meta = (DisplayName = "Offset Translation"))
    77: 	FVector ImportOffsetTranslation;
    78: 
    79: 	/** Rotation offset applied to meshes and animations. */
    80: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Common", meta = (DisplayName = "Offset Rotation"))
    81: 	FRotator ImportOffsetRotation;
    82: 
    83: 	/** Uniform scale offset applied to meshes and animations. */
    84: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Common", meta = (DisplayName = "Offset Uniform Scale"))
    85: 	float ImportOffsetUniformScale = 1.0f;
    86: 
    87: 	//////	COMMON_MESHES_CATEGORY Properties //////
    88: 	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Instanced, Category = "Common Meshes")
    89: 	TObjectPtr<UInterchangeGenericCommonMeshesProperties> CommonMeshesProperties;

## S14

[InterchangeGenericAssetsPipeline.cpp](<D:/Epic Games/UE_5.8/Engine/Plugins/Interchange/Runtime/Source/Pipelines/Private/InterchangeGenericAssetsPipeline.cpp>): D:\Epic Games\UE_5.8\Engine\Plugins\Interchange\Runtime\Source\Pipelines\Private\InterchangeGenericAssetsPipeline.cpp

    1287: 	//////////////////////////////////////////////////////////////////////////
    1288: 
    1289: 
    1290: 	//Setup the Global import offset
    1291: 	{
    1292: 		//Make sure the scale value is greater than zero, warn the user in this case and set the scale to the default value 1.0f
    1293: 		if (ImportOffsetUniformScale < UE_SMALL_NUMBER)
    1294: 		{
    1295: 			FNumberFormattingOptions FormatingOptions;
    1296: 			FormatingOptions.SetMaximumFractionalDigits(6);
    1297: 			FormatingOptions.SetMinimumFractionalDigits(1);
    1298: 			float DefaultScaleValue = 1.0f;
    1299: 			UInterchangeResultError_Generic* Message = AddMessage<UInterchangeResultError_Generic>();
    1300: 			Message->Text = FText::Format(NSLOCTEXT("UInterchangeGenericAssetsPipeline", "BadImportOffsetUniformScale", "Value [{0}] for ImportOffsetUniformScale setting is too small, we will use the default value [{1}]."),
    1301: 				FText::AsNumber(ImportOffsetUniformScale, &FormatingOptions),
    1302: 				FText::AsNumber(DefaultScaleValue, &FormatingOptions));
    1303: 			ImportOffsetUniformScale = DefaultScaleValue;
    1304: 		}
    1305: 
    1306: 		FTransform ImportOffsetTransform;
    1307: 		ImportOffsetTransform.SetTranslation(ImportOffsetTranslation);
    1308: 		ImportOffsetTransform.SetRotation(FQuat(ImportOffsetRotation));
    1309: 		ImportOffsetTransform.SetScale3D(FVector(ImportOffsetUniformScale));
    1310: 
    1311: 		UInterchangeCommonPipelineDataFactoryNode* CommonPipelineDataFactoryNode = UInterchangeCommonPipelineDataFactoryNode::FindOrCreateUniqueInstance(InBaseNodeContainer);
    1312: 		CommonPipelineDataFactoryNode->SetCustomGlobalOffsetTransform(InBaseNodeContainer, ImportOffsetTransform);
    1313: 
    1314: 		CommonPipelineDataFactoryNode->SetBakeMeshes(CommonMeshesProperties->bBakeMeshes);
    1315: 		CommonPipelineDataFactoryNode->SetBakePivotMeshes(CommonMeshesProperties->bBakePivotMeshes);
    1316: 	}
    1317: 

## S15

[InterchangeSkeletonHelper.cpp](<D:/Epic Games/UE_5.8/Engine/Plugins/Interchange/Runtime/Source/Import/Private/Mesh/InterchangeSkeletonHelper.cpp>): D:\Epic Games\UE_5.8\Engine\Plugins\Interchange\Runtime\Source\Import\Private\Mesh\InterchangeSkeletonHelper.cpp

    309: 
    310: 		SceneNode->GetCustomLocalTransform(LocalTransform);
    311: 
    312: 		const UInterchangeJointNode* JointNode = Cast<UInterchangeJointNode>(SceneNode);
    313: 		if (JointNode)
    314: 		{
    315: 			bHasTimeZeroTransform = JointNode->GetTimeZeroLocalTransform(TimeZeroLocalTransform);
    316: 			bHasBindPoseTransform = JointNode->GetBindPoseLocalTransform(BindPoseLocalTransform);
    317: 		}
    318: 
    319: 		if (ParentIndex == INDEX_NONE)
    320: 		{
    321: 			FTransform GlobalOffsetTransform = FTransform::Identity;
    322: 			bool bBakeMeshes = false;
    323: 			if (UInterchangeCommonPipelineDataFactoryNode* CommonPipelineDataFactoryNode = UInterchangeCommonPipelineDataFactoryNode::GetUniqueInstance(NodeContainer))
    324: 			{
    325: 				CommonPipelineDataFactoryNode->GetCustomGlobalOffsetTransform(GlobalOffsetTransform);
    326: 				CommonPipelineDataFactoryNode->GetBakeMeshes(bBakeMeshes);
    327: 			}
    328: 
    329: 			if (bBakeMeshes)
    330: 			{
    331: 				LocalTransform = FTransform::Identity;
    332: 				ensure(SceneNode->GetCustomGlobalTransform(NodeContainer, GlobalOffsetTransform, LocalTransform));
    333: 
    334: 				if (JointNode)
    335: 				{
    336: 					bHasTimeZeroTransform = JointNode->GetTimeZeroGlobalTransform(NodeContainer, GlobalOffsetTransform, TimeZeroLocalTransform);
    337: 					bHasBindPoseTransform = JointNode->GetBindPoseGlobalTransform(NodeContainer, GlobalOffsetTransform, BindPoseLocalTransform);
    338: 				}
    339: 			}
    340: 		}
    341: 
    342: 		Info.LocalTransform = bHasBindPoseTransform ? BindPoseLocalTransform : LocalTransform;
    343: 		//If user want to bind the mesh at time zero try to get the time zero transform
    344: 		if (bUseTimeZeroAsBindPose && bHasTimeZeroTransform)
    345: 		{
    346: 			if (bHasBindPoseTransform)
    347: 			{
    348: 				if (!TimeZeroLocalTransform.Equals(Info.LocalTransform))
    349: 				{
    350: 					bOutDiffPose = true;
    351: 				}
    352: 			}
    353: 			Info.LocalTransform = TimeZeroLocalTransform;
    354: 		}
    355: 		else if (JointNode && !GIsAutomationTesting && !bHasBindPoseTransform && !bUseTimeZeroAsBindPose)
    356: 		{
    357: 			//StaticMeshes converted to SkeletalMeshes are not expected to have BindPoses
    358: 			OutBoneNotBindNames.Add(Info.Name);
    359: 		}
    360: 

## S16

[IKRetargetProcessor.cpp](<D:/Epic Games/UE_5.8/Engine/Plugins/Animation/IKRig/Source/IKRig/Private/Retargeter/IKRetargetProcessor.cpp>): D:\Epic Games\UE_5.8\Engine\Plugins\Animation\IKRig\Source\IKRig\Private\Retargeter\IKRetargetProcessor.cpp

    28: FResolvedRetargetPose& FResolvedRetargetPoseSet::AddOrUpdateRetargetPose(
    29: 	const FRetargetSkeleton& InSkeleton,
    30: 	const FName InRetargetPoseName,
    31: 	const FIKRetargetPose* InRetargetPose,
    32: 	const FName PelvisBoneName,
    33: 	const FRetargetPoseScaleWithPivot& InSourceScale)
    34: {
    35: 	// add retarget pose if it doesn't already exist
    36: 	FResolvedRetargetPose& RetargetPose = FindOrAddRetargetPose(InRetargetPoseName);
    37: 	
    38: 	// record the version of the retarget pose (prevents re-initialization if profile swaps it)
    39: 	RetargetPose.Version = InRetargetPose->GetVersion();
    40: 	RetargetPose.PoseScale = InSourceScale;
    41: 	
    42: 	// initialize retarget pose to the skeletal mesh reference pose
    43: 	RetargetPose.LocalPose = InSkeleton.SkeletalMesh->GetRefSkeleton().GetRefBonePose();
    44: 	// copy local pose to global
    45: 	RetargetPose.GlobalPose = RetargetPose.LocalPose;
    46: 	// convert to global space
    47: 	InSkeleton.UpdateGlobalTransformsBelowBone(INDEX_NONE, RetargetPose.LocalPose, RetargetPose.GlobalPose);
    48: 
    49: 	// strip scale (done AFTER generating global pose so that scales are baked into translation)
    50: 	for (int32 BoneIndex=0; BoneIndex<InSkeleton.BoneNames.Num(); ++BoneIndex)
    51: 	{
    52: 		RetargetPose.LocalPose[BoneIndex].SetScale3D(FVector::OneVector);
    53: 		RetargetPose.GlobalPose[BoneIndex].SetScale3D(FVector::OneVector);
    54: 	}
    55: 
    56: 	// apply pelvis translation offset
    57: 	const int32 PelvisBoneIndex = InSkeleton.FindBoneIndexByName(PelvisBoneName);
    58: 	if (PelvisBoneIndex != INDEX_NONE)
    59: 	{
    60: 		FTransform& PelvisTransform = RetargetPose.GlobalPose[PelvisBoneIndex];
    61: 		PelvisTransform.AddToTranslation(InRetargetPose->GetRootTranslationDelta());
    62: 		InSkeleton.UpdateLocalTransformOfSingleBone(PelvisBoneIndex, RetargetPose.LocalPose, RetargetPose.GlobalPose);
    63: 	}
    64: 
    65: 	// apply retarget pose offsets (retarget pose is stored as offset relative to reference pose)
    66: 	const TArray<FTransform>& RefPoseLocal = InSkeleton.SkeletalMesh->GetRefSkeleton().GetRefBonePose();
    67: 	for (const TTuple<FName, FQuat>& BoneDelta : InRetargetPose->GetAllDeltaRotations())
    68: 	{
    69: 		const int32 BoneIndex = InSkeleton.FindBoneIndexByName(BoneDelta.Key);
    70: 		if (BoneIndex == INDEX_NONE)
    71: 		{
    72: 			// this can happen if a retarget pose recorded a bone offset for a bone that is not present in the
    73: 			// target skeleton; ie, the retarget pose was generated from a different Skeletal Mesh with extra bones
    74: 			continue;
    75: 		}
    76: 
    77: 		const FQuat LocalBoneRotation = RefPoseLocal[BoneIndex].GetRotation() * BoneDelta.Value;
    78: 		RetargetPose.LocalPose[BoneIndex].SetRotation(LocalBoneRotation);
    79: 	}
    80: 
    81: 	// update global transforms based on local pose modified by the retarget pose offsets
    82: 	InSkeleton.UpdateGlobalTransformsBelowBone(INDEX_NONE, RetargetPose.LocalPose, RetargetPose.GlobalPose);
    83: 
    84: 	// scale the global retarget pose
    85: 	if (RetargetPose.PoseScale.ScalePose(RetargetPose.GlobalPose))
    86: 	{
    87: 		// update the local transforms
    88: 		InSkeleton.UpdateLocalTransformsBelowBone(INDEX_NONE, RetargetPose.LocalPose, RetargetPose.GlobalPose);
    89: 	}

## S17

[AnimNode_RetargetPoseFromMesh.cpp](<D:/Epic Games/UE_5.8/Engine/Plugins/Animation/IKRig/Source/IKRig/Private/AnimNodes/AnimNode_RetargetPoseFromMesh.cpp>): D:\Epic Games\UE_5.8\Engine\Plugins\Animation\IKRig\Source\IKRig\Private\AnimNodes\AnimNode_RetargetPoseFromMesh.cpp

    175: 	
    176: 	auto ApplyRetargetedPose = [this, &Output](const TArray<FTransform>& RetargetedPose)
    177: 	{
    178: 		// convert pose to local space and apply to output
    179: 		FCSPose<FCompactPose> ComponentPose;
    180: 		ComponentPose.InitPose(Output.Pose);
    181: 		const FCompactPose& CompactPose = ComponentPose.GetPose();
    182: 		for (const TPair<int32, int32>& Pair : CompactToTargetBoneIndexMap)
    183: 		{
    184: 			const FCompactPoseBoneIndex CompactBoneIndex(Pair.Key);
    185: 			if (CompactPose.IsValidIndex(CompactBoneIndex))
    186: 			{
    187: 				const int32 TargetBoneIndex = Pair.Value;
    188: 				ComponentPose.SetComponentSpaceTransform(CompactBoneIndex, RetargetedPose[TargetBoneIndex]);
    189: 			}
    190: 		}
    191: 
    192: 		// convert to local space
    193: 		FCSPose<FCompactPose>::ConvertComponentPosesToLocalPoses(ComponentPose, Output.Pose);
    194: 
    195: 		// once converted back to local space, we copy scale values back
    196: 		// (retargeter strips scale values and deals with translation only in component space)
    197: 		const TObjectPtr<USkeletalMesh> TargetMesh = Output.AnimInstanceProxy->GetSkelMeshComponent()->GetSkeletalMeshAsset();
    198: 		const TArray<FTransform>& RefPose = TargetMesh->GetRefSkeleton().GetRefBonePose();
    199: 		for (const TPair<int32, int32>& Pair : CompactToTargetBoneIndexMap)
    200: 		{
    201: 			const FCompactPoseBoneIndex CompactBoneIndex(Pair.Key);
    202: 			if (Output.Pose.IsValidIndex(CompactBoneIndex))
    203: 			{
    204: 				const FVector ScaleFromRetarget = Output.Pose[CompactBoneIndex].GetScale3D();
    205: 				const FVector ScaleFromSkeletalMesh = RefPose[Pair.Value].GetScale3D() - FVector::OneVector;
    206: 				const FVector NewScale = ScaleFromRetarget + ScaleFromSkeletalMesh;
    207: 				Output.Pose[CompactBoneIndex].SetScale3D(NewScale);
    208: 			}
    209: 		}
    210: 	};

## S18

[RunIKRigOp.cpp](<D:/Epic Games/UE_5.8/Engine/Plugins/Animation/IKRig/Source/IKRig/Private/Retargeter/RetargetOps/RunIKRigOp.cpp>): D:\Epic Games\UE_5.8\Engine\Plugins\Animation\IKRig\Source\IKRig\Private\Retargeter\RetargetOps\RunIKRigOp.cpp

    281: 	const TArray<FTransform>& InSourceGlobalPose,
    282: 	TArray<FTransform>& OutTargetGlobalPose)
    283: {
    284: 	if (InProcessor.IsIKForcedOff() || !InProcessor.IsInitialized())
    285: 	{
    286: 		return; // skip this op when IK is off
    287: 	}
    288: 
    289: #if WITH_EDITOR
    290: 	if (GIsEditor)
    291: 	{
    292: 		// live preview source asset settings in the retarget editor
    293: 		// NOTE: this copies solver settings and goal.PositionAlpha and goal.RotationAlpha
    294: 		IKRigProcessor.CopyAllSettingsFromAsset(Settings.IKRigAsset);
    295: 	}
    296: #endif
    297: 
    298: 	FIKRigGoalContainer& GoalsFromOpStack = InProcessor.GetIKRigGoalContainer();
    299: 	
    300: 	// set main alpha on the goals
    301: 	for (FRunIKRigChain& Chain : Chains)
    302: 	{
    303: 		Chain.SetGoalAlpha(GoalsFromOpStack);
    304: 	}
    305: 
    306: 	// copy the goal container from the retargeter to the IK Rig processor
    307: 	IKRigProcessor.ApplyGoalsFromOtherContainer(GoalsFromOpStack);
    308: 	
    309: #if WITH_EDITOR
    310: 	// store initial goals transforms
    311: 	// (must be before the IK solve changes the bone transforms)
    312: 	SaveInitialGoalTransformsIntoDebugData(InProcessor, OutTargetGlobalPose);
    313: #endif
    314: 	
    315: 	// copy input pose to start IK solve from
    316: 	IKRigProcessor.SetInputPoseGlobal(OutTargetGlobalPose);
    317: 	// run IK solve
    318: 	IKRigProcessor.Solve();
    319: 	// copy results of solve
    320: 	IKRigProcessor.GetOutputPoseGlobal(OutTargetGlobalPose);
    321: 

## S19

[IKRigFullBodyIK.cpp](<D:/Epic Games/UE_5.8/Engine/Plugins/Animation/IKRig/Source/IKRig/Private/Rig/Solvers/IKRigFullBodyIK.cpp>): D:\Epic Games\UE_5.8\Engine\Plugins\Animation\IKRig\Source\IKRig\Private\Rig\Solvers\IKRigFullBodyIK.cpp

    36: 	for (int BoneIndex = 0; BoneIndex < InSkeleton.BoneNames.Num(); ++BoneIndex)
    37: 	{
    38: 		const FName& Name = InSkeleton.BoneNames[BoneIndex];
    39: 
    40: 		// get the parent bone solver index
    41: 		const int32 ParentIndex = InSkeleton.GetParentIndexThatIsNotExcluded(BoneIndex);
    42: 		const FTransform OrigTransform = InSkeleton.RefPoseGlobal[BoneIndex];
    43: 		const FVector InOrigPosition = OrigTransform.GetLocation();
    44: 		const FQuat InOrigRotation = OrigTransform.GetRotation();
    45: 		const bool bIsRoot = Name == Settings.RootBone;
    46: 		Solver.AddBone(Name, ParentIndex, InOrigPosition, InOrigRotation, bIsRoot);
    47: 	}
    48: 
    49: 	// create effectors
    50: 	for (FIKRigFBIKGoalSettings& Effector : AllGoalSettings)
    51: 	{
    52: 		Effector.IndexInSolver = Solver.AddEffector(Effector.BoneName);
    53: 	}
    54: 		
    55: 	// initialize solver
    56: 	Solver.Initialize();
    57: }
    58: 
    59: void FIKRigFullBodyIKSolver::Solve(FIKRigSkeleton& InIKRigSkeleton, const FIKRigGoalContainer& InGoals)
    60: {
    61: 	if (!Solver.IsReadyToSimulate())
    62: 	{
    63: 		return;
    64: 	}
    65: 
    66: 	if (Solver.GetNumBones() != InIKRigSkeleton.BoneNames.Num())
    67: 	{
    68: 		return;
    69: 	}
    70: 
    71: 	TArray<FTransform>& InOutTransforms = InIKRigSkeleton.CurrentPoseGlobal;
    72: 	
    73: 	// set bones to input pose
    74: 	for(int32 BoneIndex = 0; BoneIndex < Solver.GetNumBones(); BoneIndex++)
    75: 	{
    76: 		Solver.SetBoneTransform(BoneIndex, InOutTransforms[BoneIndex]);
    77: 	}
    78: 
    79: 	// update bone settings
    80: 	for (const FIKRigFBIKBoneSettings& BoneSetting : AllBoneSettings)
    81: 	{
    82: 		const int32 BoneIndex = Solver.GetBoneIndex(BoneSetting.Bone);
    83: 		if (PBIK::FBoneSettings* InternalSettings = Solver.GetBoneSettings(BoneIndex))
    84: 		{
    85: 			BoneSetting.CopyToCoreStruct(*InternalSettings);
    86: 		}
    87: 	}
    88: 
    89: 	// update effectors
    90: 	for (const FIKRigFBIKGoalSettings& GoalSettings : AllGoalSettings)
    91: 	{
    92: 		if (GoalSettings.IndexInSolver < 0)
    93: 		{
    94: 			continue;
    95: 		}
    96: 		
    97: 		const FIKRigGoal* Goal = InGoals.FindGoalByName(GoalSettings.Goal);
    98: 		if (!Goal)
    99: 		{
    100: 			return;
    101: 		}
    102: 
    103: 		PBIK::FEffectorSettings EffectorSettings;
    104: 		EffectorSettings.PositionAlpha = 1.0f; // this is constant because IKRig manages offset alphas itself
    105: 		EffectorSettings.RotationAlpha = 1.0f; // this is constant because IKRig manages offset alphas itself
    106: 		EffectorSettings.StrengthAlpha = GoalSettings.StrengthAlpha;
    107: 		EffectorSettings.ChainDepth = GoalSettings.ChainDepth;
    108: 		EffectorSettings.PullChainAlpha = GoalSettings.PullChainAlpha;
    109: 		EffectorSettings.PinRotation = GoalSettings.PinRotation;
    110: 		
    111: 		Solver.SetEffectorGoal(
    112: 			GoalSettings.IndexInSolver,
    113: 			Goal->FinalBlendedPosition,
    114: 			Goal->FinalBlendedRotation,
    115: 			EffectorSettings);
    116: 	}
    117: 
    118: 	// update settings
    119: 	FPBIKSolverSettings SolverSettings;
    120: 	SolverSettings.Iterations = Settings.Iterations;
    121: 	SolverSettings.SubIterations = Settings.SubIterations;
    122: 	SolverSettings.MassMultiplier = Settings.MassMultiplier;
    123: 	SolverSettings.bAllowStretch = Settings.bAllowStretch;
    124: 	SolverSettings.RootBehavior = Settings.RootBehavior;
    125: 	SolverSettings.PrePullRootSettings = Settings.PrePullRootSettings;
    126: 	SolverSettings.GlobalPullChainAlpha = Settings.GlobalPullChainAlpha;
    127: 	SolverSettings.MaxAngle = Settings.MaxAngle;
    128: 	SolverSettings.OverRelaxation = Settings.OverRelaxation;
    129: 
    130: 	// solve
    131: 	Solver.Solve(SolverSettings);
    132: 
    133: 	// copy transforms back
    134: 	for(int32 BoneIndex = 0; BoneIndex < Solver.GetNumBones(); BoneIndex++)
    135: 	{
    136: 		Solver.GetBoneGlobalTransform(BoneIndex, InOutTransforms[BoneIndex]);
    137: 	}
    138: }

## S20

[PBIKSolver.cpp](<D:/Epic Games/UE_5.8/Engine/Plugins/Experimental/FullBodyIK/Source/PBIK/Private/Core/PBIKSolver.cpp>): D:\Epic Games\UE_5.8\Engine\Plugins\Experimental\FullBodyIK\Source\PBIK\Private\Core\PBIKSolver.cpp

    964: void FPBIKSolver::SetBoneTransform(
    965: 	const int32 Index,
    966: 	const FTransform& InTransform)
    967: {
    968: 	check(Index >= 0 && Index < Bones.Num());
    969: 	Bones[Index].Position = InTransform.GetLocation();
    970: 	Bones[Index].Rotation = InTransform.GetRotation();
    971: 	Bones[Index].Scale = InTransform.GetScale3D();
    972: }
    973: 
    974: PBIK::FBoneSettings* FPBIKSolver::GetBoneSettings(const int32 Index)
    975: {
    976: 	// make sure to call Initialize() before applying bone settings
    977: 	if (!ensureMsgf(bReadyToSimulate, TEXT("PBIK: trying to access Bone Settings before Solver is initialized.")))
    978: 	{
    979: 		return nullptr;
    980: 	}
    981: 
    982: 	if (!ensureMsgf(Bones.IsValidIndex(Index), TEXT("PBIK: trying to access Bone Settings with invalid bone index.")))
    983: 	{
    984: 		return nullptr;
    985: 	}
    986: 
    987: 	if (!Bones[Index].Body)
    988: 	{
    989: 		// Bone is not part of the simulation. This happens if the bone is not located between an effector and the
    990: 		// root of the solver. Not necessarily an error, as some systems dynamically disable effectors which can leave
    991: 		// orphaned Bone Settings, so we simply ignore them.
    992: 		return nullptr;
    993: 	}
    994: 
    995: 	return &Bones[Index].Body->J;
    996: }
    997: 
    998: void FPBIKSolver::GetBoneGlobalTransform(const int32 Index, FTransform& OutTransform)
    999: {
    1000: 	check(Index >= 0 && Index < Bones.Num());
    1001: 	const PBIK::FBone& Bone = Bones[Index];
    1002: 	OutTransform.SetLocation(Bone.Position);
    1003: 	OutTransform.SetRotation(Bone.Rotation);
    1004: 	OutTransform.SetScale3D(Bone.Scale);
    1005: }

## S21

[PelvisMotionOp.cpp](<D:/Epic Games/UE_5.8/Engine/Plugins/Animation/IKRig/Source/IKRig/Private/Retargeter/RetargetOps/PelvisMotionOp.cpp>): D:\Epic Games\UE_5.8\Engine\Plugins\Animation\IKRig\Source\IKRig\Private\Retargeter\RetargetOps\PelvisMotionOp.cpp

    202: 	const FName TargetPelvisBoneName,
    203: 	const FTargetSkeleton& TargetSkeleton,
    204: 	FIKRigLogger& Log)
    205: {
    206: 	// validate target root bone exists
    207: 	Target.BoneName = TargetPelvisBoneName;
    208: 	Target.BoneIndex = TargetSkeleton.FindBoneIndexByName(TargetPelvisBoneName);
    209: 	if (Target.BoneIndex == INDEX_NONE)
    210: 	{
    211: 		Log.LogWarning( FText::Format(
    212: 			LOCTEXT("CountNotFindRootBone", "IK Retargeter could not find target root bone, {0} in mesh {1}"),
    213: 			FText::FromName(TargetPelvisBoneName), FText::FromString(TargetSkeleton.SkeletalMesh->GetName())));
    214: 		return false;
    215: 	}
    216: 
    217: 	const FTransform TargetInitialTransform = TargetSkeleton.RetargetPoses.GetGlobalRetargetPose()[Target.BoneIndex];
    218: 	Target.InitialHeight = static_cast<float>(TargetInitialTransform.GetTranslation().Z);
    219: 	Target.InitialRotation = TargetInitialTransform.GetRotation();
    220: 	Target.InitialPosition = TargetInitialTransform.GetTranslation();
    221: 
    222: 	// initialize the global scale factor
    223: 	const float ScaleFactor = Source.InitialHeightInverse * Target.InitialHeight;
    224: 	GlobalScaleFactor.Set(ScaleFactor, ScaleFactor, ScaleFactor);
    225: 	
    226: 	return true;
    227: }

## S22

[IKRigAutoFBIK.cpp](<D:/Epic Games/UE_5.8/Engine/Plugins/Animation/IKRig/Source/IKRigEditor/Private/RigEditor/IKRigAutoFBIK.cpp>): D:\Epic Games\UE_5.8\Engine\Plugins\Animation\IKRig\Source\IKRigEditor\Private\RigEditor\IKRigAutoFBIK.cpp

    13: void FAutoFBIKCreator::CreateFBIKSetup(const UIKRigController& IKRigController, FAutoFBIKResults& Results) const
    14: {
    15: 	// ensure we have a mesh to operate on
    16: 	USkeletalMesh* Mesh = IKRigController.GetSkeletalMesh();
    17: 	if (!Mesh)
    18: 	{
    19: 		Results.Outcome = EAutoFBIKResult::MissingMesh;
    20: 		return;
    21: 	}
    22: 
    23: 	// auto generate a retarget definition
    24: 	FAutoCharacterizeResults CharacterizeResults;
    25: 	IKRigController.AutoGenerateRetargetDefinition(CharacterizeResults);
    26: 	if (!CharacterizeResults.bUsedTemplate)
    27: 	{
    28: 		Results.Outcome = EAutoFBIKResult::UnknownSkeletonType;
    29: 		return;
    30: 	}
    31: 	
    32: 	// create all the goals in the template
    33: 	TArray<FName> GoalNames;
    34: 	const TArray<FBoneChain>& ExpectedChains = CharacterizeResults.AutoRetargetDefinition.RetargetDefinition.BoneChains;
    35: 	for (const FBoneChain& ExpectedChain : ExpectedChains)
    36: 	{
    37: 		if (ExpectedChain.IKGoalName == NAME_None)
    38: 		{
    39: 			continue;
    40: 		}
    41: 		
    42: 		const FBoneChain* Chain = IKRigController.GetRetargetChainByName(ExpectedChain.ChainName);
    43: 		FName GoalName = (Chain && Chain->IKGoalName != NAME_None) ? Chain->IKGoalName : ExpectedChain.IKGoalName;
    44: 		const UIKRigEffectorGoal* ChainGoal = IKRigController.GetGoal(GoalName);
    45: 		if (!ChainGoal)
    46: 		{
    47: 			// create new goal
    48: 			GoalName = IKRigController.AddNewGoal(GoalName, ExpectedChain.EndBone.BoneName);
    49: 			if (Chain)
    50: 			{
    51: 				IKRigController.SetRetargetChainGoal(Chain->ChainName, GoalName);
    52: 			}
    53: 			else
    54: 			{
    55: 				UE_LOGF(LogIKRigEditor, Warning, "Auto FBIK created goal for a limb, but it did not have a retarget chain. %ls", *ExpectedChain.ChainName.ToString());
    56: 			}
    57: 		}
    58: 
    59: 		GoalNames.Add(GoalName);
    60: 	}
    61: 
    62: 	// create IK solver and attach all the goals to it
    63: 	const int32 SolverIndex = IKRigController.AddSolver(FIKRigFullBodyIKSolver::StaticStruct());
    64: 	for (const FName& GoalName : GoalNames)
    65: 	{
    66: 		IKRigController.ConnectGoalToSolver(GoalName, SolverIndex);	
    67: 	}
    68: 
    69: 	// set the root of the solver
    70: 	const bool bSetRoot = IKRigController.SetStartBone(CharacterizeResults.AutoRetargetDefinition.RetargetDefinition.PelvisBone, SolverIndex);
    71: 	if (!bSetRoot)
    72: 	{
    73: 		Results.Outcome = EAutoFBIKResult::MissingPelvisBone;
    74: 		return;
    75: 	}
    76: 
    77: 	// update solver settings for retargeting
    78: 	FIKRigFullBodyIKSolver* Solver = static_cast<FIKRigFullBodyIKSolver*>(IKRigController.GetSolverAtIndex(SolverIndex));
    79: 	// set the root behavior to "free", allows pelvis motion only when needed to reach goals
    80: 	Solver->Settings.RootBehavior = EPBIKRootBehavior::Free;
    81: 	// removing pull chain alpha on all goals "calms" the motion down, especially when retargeting arms
    82: 	Solver->Settings.GlobalPullChainAlpha = 0.0f;
    83: 	// sub-iterations for chain-level sub-solves before each main iteration
    84: 	Solver->Settings.SubIterations = 10;
    85: 

## S23

[MeshWrapNode.h](<D:/Epic Games/UE_5.8/Engine/Plugins/Experimental/MeshResizing/Source/MeshResizingNodes/Public/MeshResizing/MeshWrapNode.h>): D:\Epic Games\UE_5.8\Engine\Plugins\Experimental\MeshResizing\Source\MeshResizingNodes\Public\MeshResizing\MeshWrapNode.h

    17: /**
    18:  * Mesh Wrap Node landmark. Matched landmarks between source topology and target shape meshes are used to guide the Mesh Wrap operation.
    19:  */
    20: USTRUCT()
    21: struct FMeshWrapLandmark
    22: {
    23: 	GENERATED_USTRUCT_BODY()
    24: 
    25: 	/** String name. Landmarks will be matched by comparing identifiers.*/
    26: 	UPROPERTY(EditAnywhere, Category = "Mesh Wrap")
    27: 	FString Identifier;
    28: 
    29: 	/** Vertex of this landmark. */
    30: 	UPROPERTY(EditAnywhere, Category = "Mesh Wrap", meta = (ClampMin = "-1"))
    31: 	int32 VertexIndex = INDEX_NONE;
    32: };
    33: 
    34: /**
    35:  * Matched Mesh Wrap Node landmark correspondence.
    36:  */
    37: USTRUCT()
    38: struct FMeshWrapCorrespondence
    39: {
    40: 	GENERATED_USTRUCT_BODY()
    41: 
    42: 	/** Matched landmark name.*/
    43: 	UPROPERTY(EditAnywhere, Category = "Mesh Wrap")
    44: 	FString Identifier;
    45: 
    46: 	/** Vertex on source topology mesh.*/
    47: 	UPROPERTY(EditAnywhere, Category = "Mesh Wrap", meta = (ClampMin = "-1"))
    48: 	int32 SourceVertexIndex = INDEX_NONE;
    49: 
    50: 	/** Vertex on target shape mesh. */
    51: 	UPROPERTY(EditAnywhere, Category = "Mesh Wrap", meta = (ClampMin = "-1"))
    52: 	int32 TargetVertexIndex = INDEX_NONE;
    53: };
    54: 
    55: /** Node for defining landmarks used by MeshWrapNode. The Mesh Wrap Landmark Selection Tool allows generating these landmarks via selection. */
    56: USTRUCT(Meta = (MeshResizing, Experimental))
    57: struct FMeshWrapLandmarksNode : public FDataflowNode
    58: {

    115: 
    116: public:
    117: 
    118: 	FMeshWrapNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid());
    119: 
    120: private:
    121: 
    122: 	/** Input mesh with the desired wrapped mesh topology. */
    123: 	UPROPERTY(meta = (DataflowInput))
    124: 	TObjectPtr<UDataflowMesh> SourceTopologyMesh;
    125: 
    126: 	/** Input mesh with the desired wrapped mesh shape. */
    127: 	UPROPERTY(meta = (DataflowInput))
    128: 	TObjectPtr<UDataflowMesh> TargetShapeMesh;
    129: 
    130: 	/** Output wrapped mesh. */
    131: 	UPROPERTY(meta = (DataflowOutput, DataflowPassthrough = "SourceTopologyMesh"))
    132: 	TObjectPtr<UDataflowMesh> WrappedMesh;
    133: 
    134: 	/** Landmarks defined on SourceTopologyMesh. TargetShapeLandmarks with matching Identifiers will be used to find correspondences that help improve the wrap. */
    135: 	UPROPERTY(EditAnywhere, Category = "Mesh Wrap", meta = (DataflowInput))
    136: 	TArray<FMeshWrapLandmark> SourceTopologyLandmarks;
    137: 
    138: 	/** Landmarks defined on TargetShapeMesh. SourceTopologyLandmarks with matching Identifiers will be used to find correspondences that help improve the wrap. */
    139: 	UPROPERTY(EditAnywhere, Category = "Mesh Wrap", meta = (DataflowInput))
    140: 	TArray<FMeshWrapLandmark> TargetShapeLandmarks;
    141: 
    142: 	/** Landmarks matched by Identifier from SourceTopologyLandmarks and TargetShapeLandmarks. */
    143: 	UPROPERTY(meta = (DataflowOutput))
    144: 	TArray<FMeshWrapCorrespondence> MatchedLandmarks;
    145: 
    146: 	/** Mesh Wrap is calculated with an inner and outer loop. This is the maximum number of outer loops. Each outer loop increases the Projection Stiffness by ProjectionStiffnessMultiplier.*/
    147: 	UPROPERTY(EditAnywhere, Category = "Mesh Wrap", Meta = (ClampMin ="0"))
    148: 	int32 MaxNumOuterIterations = 10;
    149: 
    150: 	/** Mesh Wrap is calculated with an inner and outer loop. This is the number of inner loops run before increasing the Projection Stiffness in the outer loop.*/
    151: 	UPROPERTY(EditAnywhere, Category = "Mesh Wrap", Meta = (ClampMin = "0"))
    152: 	int32 NumInnerIterations = 20;
    153: 
    154: 	/** Mesh Wrap will terminate early if the Projection tolerance is within this threshold.*/
    155: 	UPROPERTY(EditAnywhere, Category = "Mesh Wrap", Meta =(ClampMin = "0"))
    156: 	float ProjectionTolerance = 1e-4f;
    157: 
    158: 	/** Weight of mesh wrap to retain Source Topology mesh features.*/
    159: 	UPROPERTY(EditAnywhere, Category = "Mesh Wrap", AdvancedDisplay, Meta = (ClampMin = "0"))
    160: 	float LaplacianStiffness = 1.;
    161: 
    162: 	/** Initial weight of mesh wrap to match projected Target Shape. Each outer loop will multiply this stiffness by ProjectionStiffnessMultiplier.*/
    163: 	UPROPERTY(EditAnywhere, Category = "Mesh Wrap", AdvancedDisplay, Meta = (ClampMin = "0"))
    164: 	float InitialProjectionStiffness = 0.1f;
    165: 	
    166: 	/** Each outer loop will multiply InitialProjectionStiffness by this to improve Target Shape match.*/
    167: 	UPROPERTY(EditAnywhere, Category = "Mesh Wrap", AdvancedDisplay, Meta = (ClampMin = "0"))
    168: 	float ProjectionStiffnessMuliplier = 10.;
    169: 
    170: 	/** Weight of mesh wrap to match Landmark correspondences.*/
    171: 	UPROPERTY(EditAnywhere, Category = "Mesh Wrap", AdvancedDisplay, Meta = (ClampMin = "0"))
    172: 	float CorrespondenceStiffness = 1.;
    173: 
    174: 	/** Display material for Source or Target when none is supplied. */
    175: 	UPROPERTY(EditAnywhere, Category = "Mesh Wrap Display")
    176: 	TObjectPtr<UMaterial> DefaultDisplayMaterial;
    177: 
    178: 	/** Display landmarks. */
    179: 	UPROPERTY(EditAnywhere, Category = "Mesh Wrap Display")
    180: 	bool bDisplayLandmarks = true;
    181: 

## S24

[MeshWrapNode.cpp](<D:/Epic Games/UE_5.8/Engine/Plugins/Experimental/MeshResizing/Source/MeshResizingNodes/Private/MeshResizing/MeshWrapNode.cpp>): D:\Epic Games\UE_5.8\Engine\Plugins\Experimental\MeshResizing\Source\MeshResizingNodes\Private\MeshResizing\MeshWrapNode.cpp

    189: void FMeshWrapNode::Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const
    190: {
    191: 	using namespace UE::Geometry;
    192: 
    193: 	if (Out->IsA<TArray<FMeshWrapCorrespondence>>(&MatchedLandmarks))
    194: 	{
    195: 		SetValue(Context, CalculateMatchedLandmarks(Context), &MatchedLandmarks);
    196: 		return;
    197: 	}
    198: 
    199: 	if (Out->IsA(&WrappedMesh))
    200: 	{
    201: 		if (TObjectPtr<UDataflowMesh> InSourceTopologyMesh = GetValue(Context, &SourceTopologyMesh))
    202: 		{
    203: 			if (TObjectPtr<UDataflowMesh> InTargetShapeMesh = GetValue(Context, &TargetShapeMesh))
    204: 			{
    205: 				if (InSourceTopologyMesh->GetDynamicMesh() && InTargetShapeMesh->GetDynamicMesh())
    206: 				{
    207: 					const TArray<FMeshWrapCorrespondence>& InMatchedLandmarks = GetOutputValue(Context, &MatchedLandmarks, TArray<FMeshWrapCorrespondence>());
    208: 					TArray<FWrapMeshCorrespondence> Correspondences;
    209: 					Correspondences.Reserve(InMatchedLandmarks.Num());
    210: 					for (const FMeshWrapCorrespondence& MatchedLandmark : InMatchedLandmarks)
    211: 					{
    212: 						Correspondences.Emplace(MatchedLandmark.SourceVertexIndex, MatchedLandmark.TargetVertexIndex);
    213: 					}
    214: 					TObjectPtr<UDataflowMesh> OutWrappedMesh = NewObject<UDataflowMesh>();
    215: 					FDynamicMesh3 WrappedFMesh;
    216: 					FWrapMesh MeshWrapper(nullptr);
    217: 					MeshWrapper.MaxNumOuterIterations = MaxNumOuterIterations;
    218: 					MeshWrapper.NumInnerIterations = NumInnerIterations;
    219: 					MeshWrapper.ProjectionTolerance = ProjectionTolerance;
    220: 					MeshWrapper.LaplacianStiffness = LaplacianStiffness;
    221: 					MeshWrapper.InitialProjectionStiffness = InitialProjectionStiffness;
    222: 					MeshWrapper.ProjectionStiffnessMuliplier = ProjectionStiffnessMuliplier;
    223: 					MeshWrapper.CorrespondenceStiffness = CorrespondenceStiffness;
    224: 					MeshWrapper.LaplacianType = FWrapMesh::ELaplacianType::AffineInvariant;
    225: 					MeshWrapper.SetMesh(InSourceTopologyMesh->GetDynamicMesh());
    226: 
    227: 					MeshWrapper.WrapToTargetShape(InTargetShapeMesh->GetDynamicMeshRef(), Correspondences, WrappedFMesh);
    228: 					OutWrappedMesh->SetDynamicMesh(MoveTemp(WrappedFMesh));
    229: 					OutWrappedMesh->SetMaterials(InSourceTopologyMesh->GetMaterials());
    230: 					SetValue(Context, OutWrappedMesh, &WrappedMesh);
    231: 
    232: 					return;
    233: 				}
    234: 			}
    235: 
    236: 		}
    237: 
    238: 		SafeForwardInput(Context, &SourceTopologyMesh, &WrappedMesh);
    239: 	}

## S25

[RBFInterpolationNodes.h](<D:/Epic Games/UE_5.8/Engine/Plugins/Experimental/MeshResizing/Source/MeshResizingNodes/Private/MeshResizing/RBFInterpolationNodes.h>): D:\Epic Games\UE_5.8\Engine\Plugins\Experimental\MeshResizing\Source\MeshResizingNodes\Private\MeshResizing\RBFInterpolationNodes.h

    62: USTRUCT(Meta = (MeshResizing, Experimental))
    63: struct FApplyRBFResizingNode : public FDataflowNode
    64: {
    65: 	GENERATED_USTRUCT_BODY()
    66: 	DATAFLOW_NODE_DEFINE_INTERNAL(FApplyRBFResizingNode, "ApplyRBFResizing", "MeshResizing", "Apply RBF Resizing")
    67: 
    68: public:
    69: 	FApplyRBFResizingNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid());
    70: 
    71: private:
    72: 
    73: 	/** The mesh being resized */
    74: 	UPROPERTY(meta = (DataflowInput))
    75: 	TObjectPtr<const UDataflowMesh> MeshToResize;
    76: 
    77: #if WITH_EDITORONLY_DATA
    78: 	// Skeletal mesh target requires access to the MeshDescription, which is Editor-only
    79: 	/** Use a skeletal mesh for the target mesh (instead of a dynamic mesh)*/
    80: 	UPROPERTY(EditAnywhere, Category = "RBF Resize")
    81: 	bool bUseSkeletalMeshTarget = false;
    82: #else
    83: 	static constexpr bool bUseSkeletalMeshTarget = false;
    84: #endif
    85: 
    86: 	/** The target mesh that corresponds with the SourceMesh used to generate the InterpolationData. Must have matching vertices with SourceMesh */
    87: 	UPROPERTY(meta = (DataflowInput, EditCondition = "bUseSkeletalMeshTarget"))
    88: 	TObjectPtr<const USkeletalMesh> TargetSkeletalMesh;
    89: 
    90: 	UPROPERTY(EditAnywhere, Category = "RBF Resize", meta = (DataflowInput, EditCondition = "bUseSkeletalMeshTarget", ClampMin = 0))
    91: 	int32 TargetSkeletalMeshLODIndex = 0;
    92: 
    93: 	/** The target mesh that corresponds with the SourceMesh used to generate the InterpolationData. Must have matching vertices with SourceMesh */
    94: 	UPROPERTY(meta = (DataflowInput, EditCondition = "!bUseSkeletalMeshTarget"))
    95: 	TObjectPtr<const UDataflowMesh> TargetMesh;
    96: 
    97: 	/** The pre-calculated base RBF interpolation data.*/
    98: 	UPROPERTY(meta = (DataflowInput))
    99: 	FMeshResizingRBFInterpolationData InterpolationData;
    100: 
    101: 	/** The resulting resized mesh */
    102: 	UPROPERTY(meta = (DataflowOutput, DataflowPassthrough = "MeshToResize"))
    103: 	TObjectPtr<const UDataflowMesh> ResizedMesh;
    104: 
    105: 	/** Whether or not to interpolate the normals as well as the positions*/
    106: 	UPROPERTY(EditAnywhere, Category = "RBF Resize")
    107: 	bool bInterpolateNormals = true;
    108: 
    109: 	//~ Begin FDataflowNode interface
    110: 	virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override;
    111: 	//~ End FDataflowNode interface
    112: };

## S26

[SkeletonModifier.h](<D:/Epic Games/UE_5.8/Engine/Plugins/Runtime/MeshModelingToolset/Source/SkeletalMeshModifiers/Public/SkeletonModifier.h>): D:\Epic Games\UE_5.8\Engine\Plugins\Runtime\MeshModelingToolset\Source\SkeletalMeshModifiers\Public\SkeletonModifier.h

    127: class USkeletonModifier : public UObject
    128: {
    129: 	GENERATED_BODY()
    130: 	
    131: public:
    132: 
    133: 	UFUNCTION(BlueprintCallable, Category = "Mesh")
    134: 	UE_API bool SetSkeletalMesh(USkeletalMesh* InSkeletalMesh);
    135: 	
    136: 	/**
    137: 	 * Applies the skeleton modifications to the skeletal mesh.
    138: 	 * @return true if commit succeeded.
    139: 	 */
    140: 	UFUNCTION(BlueprintCallable, Category = "Mesh")
    141: 	UE_API bool CommitSkeletonToSkeletalMesh();
    142: 
    143: 
    144: 	UE_API bool SetDynamicMesh(UDynamicMesh* InDynamicMesh);
    145: 
    146: 	UE_API bool SetReferenceSkeleton(const FReferenceSkeleton& InReferenceSkeleton);
    147: 	
    148: 	UE_API void SetReadOnly(bool bInReadOnly);
    149: 	UE_API bool IsReadOnly() const;

    179: 	/** Sets the bone the desired local transform
    180: 	 *  @param InBoneName The new bone's name that needs to be moved.
    181: 	 *  @param InNewTransform The new local transform in the bone's parent space.
    182: 	 *  @param bMoveChildren Propagate new transform to children
    183: 	 *  @return \c true if the operation succeeded, false otherwise. 
    184: 	 */
    185: 	UFUNCTION(BlueprintCallable, Category = "Skeleton")
    186: 	UE_API bool SetBoneTransform(const FName InBoneName, const FTransform& InNewTransform, const bool bMoveChildren);
    187: 	UFUNCTION(BlueprintCallable, Category = "Skeleton")
    188: 	UE_API bool SetBonesTransforms(const TArray<FName>& InBoneNames, const TArray<FTransform>& InNewTransforms, const bool bMoveChildren);
    189: 
    190: 	/** Remove a bone in the skeleton hierarchy
    191: 	 *  @param InBoneName The new bone's name.
    192: 	 *  @param bRemoveChildren Remove children recursively.
    193: 	 *  @return \c true if the operation succeeded, false otherwise. 
    194: 	 */

## S27

[ScaleSourceOp.h](<D:/Epic Games/UE_5.8/Engine/Plugins/Animation/IKRig/Source/IKRig/Public/Retargeter/RetargetOps/ScaleSourceOp.h>): D:\Epic Games\UE_5.8\Engine\Plugins\Animation\IKRig\Source\IKRig\Public\Retargeter\RetargetOps\ScaleSourceOp.h

    20: USTRUCT(BlueprintType, meta = (DisplayName = "Scale Source Settings"))
    21: struct FIKRetargetScaleSourceOpSettings : public FIKRetargetOpSettingsBase
    22: {
    23: 	GENERATED_BODY()
    24: 	
    25: 	/** Range 0.01 to +inf. Default 1. Scales the incoming source pose. Affects entire skeleton and all IK goals.*/
    26: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Op Settings", meta = (ReinitializeOnEdit, ClampMin = "0.01", UIMin = "0.01", UIMax = "10.0"))
    27: 	double SourceScaleFactor = 1.0f;
    28: 
    29: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Op Settings")
    30: 	EScaleSourcePivot ScalePivot = EScaleSourcePivot::ComponentOrigin;
    31: 
    32: 	UPROPERTY(EditAnywhere, Category = "Op Settings", meta=(NotOverrideable))
    33: 	FBoneReference ScalePivotBone;
    34: 
    35: 	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Op Settings")
    36: 	bool bProjectScalePivotToFloor = false;
    37: 
    38: 	UE_API virtual const UClass* GetControllerType() const override;
    39: 
    40: 	UE_API virtual void CopySettingsAtRuntime(const FIKRetargetOpSettingsBase* InSettingsToCopyFrom) override;
    41: 
    42: #if WITH_EDITORONLY_DATA
    43: 	virtual USkeleton* GetSkeleton(const FName InPropertyName) override;
    44: #endif
    45: };
    46: 
    47: USTRUCT(BlueprintType, meta = (DisplayName = "Scale Source"))
    48: struct FIKRetargetScaleSourceOp : public FIKRetargetOpBase
    49: {
    50: 	GENERATED_BODY()
    51: 	
    52: 	// NOTE: this op does not do anything in Initialize() or Run().
    53: 	// It is a special case op that the retargeter reads from when it needs to scale the source pose.
    54: 	
    55: 	UE_API virtual bool Initialize(
    56: 		const FIKRetargetProcessor& InProcessor,
    57: 		const FRetargetSkeleton& InSourceSkeleton,
    58: 		const FTargetSkeleton& InTargetSkeleton,
    59: 		const FIKRetargetOpBase* InParentOp,
    60: 		FIKRigLogger& Log) override;
    61: 	
    62: 	virtual void Run(
    63: 		FIKRetargetProcessor& InProcessor,
    64: 		const double InDeltaTime,
    65: 		const TArray<FTransform>& InSourceGlobalPose,

## S28

[UfbxParser.cpp](<D:/Epic Games/UE_5.8/Engine/Plugins/Interchange/Runtime/Source/Parsers/Fbx/Private/Ufbx/UfbxParser.cpp>): D:\Epic Games\UE_5.8\Engine\Plugins\Interchange\Runtime\Source\Parsers\Fbx\Private\Ufbx\UfbxParser.cpp

    99: 
    100: 	// #ufbx_todo:
    101: 	// LoadOpts.inherit_mode_handling
    102: 
    103: 	// #ufbx_todo:
    104: 	// LoadOpts.pivot_handling
    105: 
    106: 	LoadOpts.space_conversion = UFBX_SPACE_CONVERSION_ADJUST_TRANSFORMS;
    107: 
    108: 
    109: 	if (bForceFrontXAxis)
    110: 	{
    111: 		// When X for front 
    112: 		LoadOpts.target_axes = ufbx_coordinate_axes{
    113: 	UFBX_COORDINATE_AXIS_NEGATIVE_Y, UFBX_COORDINATE_AXIS_POSITIVE_Z, UFBX_COORDINATE_AXIS_POSITIVE_X,
    114: 		};
    115: 	}
    116: 	else	
    117: 	{
    118: 		LoadOpts.target_axes = ufbx_axes_left_handed_z_up;
    119: 	}
    120: 	LoadOpts.handedness_conversion_axis = UFBX_MIRROR_AXIS_Y;
    121: 
    122: 	LoadOpts.target_unit_meters = 0.01; // Centimeters
    123: 	LoadOpts.reverse_winding = true;
    124: 
    125: 	LoadOpts.target_camera_axes.front = UFBX_COORDINATE_AXIS_NEGATIVE_X;

## S29

[example_auto_rig.py](<D:/Epic Games/UE_5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter/Content/Python/examples/example_auto_rig.py>): D:\Epic Games\UE_5.8\Engine\Plugins\MetaHuman\MetaHumanCharacter\Content\Python\examples\example_auto_rig.py

    1: import unreal
    2: 
    3: # Load the asset
    4: character = unreal.load_asset("/Game/Characters/MetaHumans/Jeff.Jeff")
    5: 
    6: # Get the MetaHuman Subsystem
    7: metahuman_subsystem = unreal.get_editor_subsystem(
    8:     unreal.MetaHumanCharacterEditorSubsystem
    9: )
    10: 
    11: # Try to edit the character
    12: if not metahuman_subsystem.try_add_object_to_edit(character):
    13:     raise RuntimeError("Unable to edit asset, is it already open for edit?")
    14: 
    15: try:
    16:     auto_rigging_request = unreal.MetaHumanCharacterAutoRiggingRequestParams()
    17:     # Required for running in batch
    18:     auto_rigging_request.blocking = True
    19:     auto_rigging_request.report_progress = False
    20:     # Rig Types are JOINTS_ONLY or JOINTS_AND_BLENDSHAPES
    21:     auto_rigging_request.rig_type = unreal.MetaHumanRigType.JOINTS_ONLY
    22:     metahuman_subsystem.request_auto_rigging(character, auto_rigging_request)
    23: 
    24:     # Optional: tear the rig back down. Resets the face mesh to the archetype DNA
    25:     # and unregisters any morph targets, leaving the character editable again.
    26:     # metahuman_subsystem.remove_face_rig(character)
    27: 
    28: finally:
    29:     # Finish Editing
    30:     if metahuman_subsystem.is_object_added_for_editing(character):
    31:         metahuman_subsystem.remove_object_to_edit(character)

## S30

[MetaHumanIdentityParts.h](<D:/Epic Games/UE_5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanIdentity/Public/MetaHumanIdentityParts.h>): D:\Epic Games\UE_5.8\Engine\Plugins\MetaHuman\MetaHumanAnimator\Source\MetaHumanIdentity\Public\MetaHumanIdentityParts.h

    90: 
    91: UENUM()
    92: enum class EConformType
    93: {
    94: 	/** Use the Face Fitting conformer, i.e. FitIdentity */
    95: 	Solve,
    96: 
    97: 	/**
    98: 	 * Copy the data from the Neutral Pose face mesh to the Template Mesh.
    99: 	 * Assumes the target mesh is already conformed and in the correct topology
    100: 	 * expected by the Mesh To MetaHuman service 
    101: 	 */
    102: 	Copy,
    103: };
    104: 
    105: UCLASS(MinimalAPI, HideCategories = ("Preview"))
    106: class UMetaHumanIdentityFace
    107: 	: public UMetaHumanIdentityPart
    108: {
    109: 	GENERATED_BODY()
    110: 
    111: public:
    112: 	UE_API UMetaHumanIdentityFace();
    113: 
    114: 	//~UMetaHumanIdentityFace Interface
    115: 	UE_API virtual void Initialize() override;
    116: 	UE_API virtual FText GetPartName() const override;
    117: 	UE_API virtual FText GetPartDescription() const override;
    118: 	UE_API virtual FSlateIcon GetPartIcon(const FName& InPropertyName = NAME_None) const override;
    119: 	UE_API virtual FText GetPartTooltip(const FName& InPropertyName = NAME_None) const override;
    120: 	UE_API virtual bool DiagnosticsIndicatesProcessingIssue(FText& OutDiagnosticsWarningMessage) const override;
    121: 
    122: 	//~UObject Interface
    123: 	UE_API virtual void PostLoad() override;
    124: 	UE_API virtual void Serialize(FArchive& Ar) override;
    125: 
    126: #if WITH_EDITOR
    127: 	UE_API virtual void PostEditChangeProperty(struct FPropertyChangedEvent& InPropertyChangedEvent) override;
    128: #endif
    129: 
    130: 	/** Return true if the face has all the required information to run the MetaHuman Identity solve (conforming) */
    131: 	UE_API bool CanConform() const;
    132: 
    133: 	/** Return true if the face can be submitted to the AutoRigging service, which means is already conformed and the Neutral Pose has a valid Capture Data */
    134: 	UE_API bool CanSubmitToAutorigging() const;
    135: 
    136: 	/** MetaHuman Identity solve */
    137: 	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Solve")
    138: 	UE_API EIdentityErrorCode Conform(EConformType InConformType = EConformType::Solve);
    139: 
    140: 	/** Returns true if the conformal rig component is valid and points to a valid skeletal mesh */
    141: 	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Rig")
    142: 	UE_API bool IsConformalRigValid() const;
