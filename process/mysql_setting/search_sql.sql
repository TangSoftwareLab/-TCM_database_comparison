# TCM-id
SELECT count(*) FROM tcm_id.tcm_plant_ingredient_pairs_allingredients;
SELECT count(distinct(Plant_ID)) FROM tcm_id.tcm_plant_ingredient_pairs_allingredients;
SELECT count(distinct(cp_i.Ingredient_ID)) FROM tcm_id.tcm_plant_ingredient_pairs_allingredients;

SELECT count(*) FROM tcm_id.tcm_ingredients_tar_activi;
SELECT count(distinct(Ingredient_ID)) FROM tcm_id.tcm_ingredients_tar_activi;
SELECT count(distinct(Target_ID)) FROM tcm_id.tcm_ingredients_tar_activi;

SELECT count(*) FROM tcm_id.disease_info;

SELECT count(*) FROM tcm_id.herb_targeted_human_proteins;
SELECT count(distinct(`Herb ID`)) FROM tcm_id.herb_targeted_human_proteins;
SELECT count(distinct(`Targeted_Human_Proteins`)) FROM tcm_id.herb_targeted_human_proteins;

SELECT count(*) FROM tcm_id.herb_targeted_pathogenic_microbes;
SELECT count(distinct(`Herb ID`)) FROM tcm_id.herb_targeted_pathogenic_microbes;
SELECT count(distinct(Targeted_Pathogenic_Microbes)) FROM tcm_id.herb_targeted_pathogenic_microbes;

SELECT count(*) FROM tcm_id.tcm_ingredients_tar_activi;
SELECT count(distinct(Ingredient_ID)) FROM tcm_id.tcm_ingredients_tar_activi;
SELECT count(distinct(Target_ID)) FROM tcm_id.tcm_ingredients_tar_activi;

SELECT count(*) FROM tcm_id.cp_targets;
SELECT count(*) FROM tcm_id.formulae_indications;

SELECT count(*) FROM tcm_id.cp_ingredients_onlyactive;

SELECT count(*) FROM tcm_id.formulae_indications;
SELECT count(distinct(`Prescription ID`)) FROM tcm_id.formulae_indications;
SELECT count(distinct(Indications)) FROM tcm_id.formulae_indications;

SELECT count(*) FROM tcm_id.formulae_function_description;
SELECT count(distinct(`Prescription ID`)) FROM tcm_id.formulae_function_description;
SELECT count(distinct(`Function Description`)) FROM tcm_id.formulae_function_description;


SELECT
*
FROM
tcm_id.cp_plant_ingredient_pairs_allingredients as h,
tcm_id.herb_detail as d,
tcm_id.cp_plants as p,
tcm_id.cp_ingredients_all as cp_i
where
h.Plant_ID = p.Plant_ID
and p.Plant_Name = d.`Latin Name`
and p.Plant_ID = h.Plant_ID
and h.Ingredient_ID = cp_i.Ingredient_ID;

SELECT
*
FROM
tcm_id.tcm_plant_ingredient_pairs_allingredients as h_i,
tcm_id.cp_ingredient_target_pairs_activityvalues_references as c_i_acti
where
h_i.Ingredient_ID = cp_i.Ingredient_ID;

SELECT
*
FROM
tcm_id.cp_plant_ingredient_pairs_allingredients as h,
tcm_id.herb_detail as d,
tcm_id.cp_plants as p,
tcm_id.cp_plant_ingredient_pairs_allingredients as h_i_p,
tcm_id.cp_ingredients_all as cp_i
where
h.Plant_ID = p.Plant_ID
and p.Plant_Name = d.`Latin Name`
and h_i_p.Plant_ID = h.Plant_ID
and h_i_p.Ingredient_ID = cp_i.Ingredient_ID;


SELECT
*
FROM
tcm_id.cp_plant_ingredient_pairs_allingredients as h,
tcm_id.herb_detail as d,
tcm_id.cp_plants as p,
tcm_id.cp_plant_ingredient_pairs_allingredients as h_i_p,
tcm_id.cp_ingredients_all as cp_i,
tcm_id.herb_targeted_human_proteins as h_p_1,
tcm_id.herb_targeted_pathogenic_microbes as h_t
where
h.Plant_ID = p.Plant_ID
and p.Plant_Name = d.`Latin Name`
and h_i_p.Plant_ID = h.Plant_ID
and h_i_p.Ingredient_ID = cp_i.Ingredient_ID;


SELECT * FROM tcm_id.tcm_herb_new as h, 
tcm_id.herb_targeted_pathogenic_microbes as h_t_m,
tcm_id.cp_targets as t 
where h.中文名 = '紫草' 
and h_t_m.`Herb ID` =  h.`Component ID` 
and h_t_m.Targeted_Pathogenic_Microbes =  t.Target_ID;
 ;


SELECT * FROM tcm_id.tcm_herb_new as h,
tcm_id.herb_targeted_human_proteins as h_t_h,
tcm_id.cp_targets as t 
where h.中文名 = '紫草' 
and h_t_h.`Herb ID` =  h.`Component ID` 
and h_t_h.Targeted_Human_Proteins =  t.Target_ID;


## TCMSP

SELECT count(*) FROM tcmsp.molecules_targets_relationships;

SELECT count(distinct(tcmsp_ingredient_id)) FROM tcmsp.molecules_targets_relationships;

SELECT count(distinct(tcmsp_target_id)) FROM tcmsp.molecules_targets_relationships;

SELECT count(*) FROM tcmsp.herbs_molecules_relationships;

SELECT count(distinct(tcmsp_herb_id)) FROM tcmsp.herbs_molecules_relationships;

SELECT count(distinct(tcmsp_ingredient_id)) FROM tcmsp.herbs_molecules_relationships;


SELECT * FROM new_herb as h,
new_molecular_info as m,
info_targets as t, 
herbs_molecules_relationships as h_m
where h.tcmsp_herb_cn_name = '紫草'
and h.tcmsp_herb_id = h_m.tcmsp_herb_id
and m.tcmsp_ingredient_id = h_m.tcmsp_ingredient_id
;

use tcmsp;
SELECT * FROM new_molecular_info as m,
info_targets as t,
molecules_targets_relationships as m_t
where m.tcmsp_ingredient_id = 'MOL000004'
and m_t.tcmsp_ingredient_id = m.tcmsp_ingredient_id
and m_t.tcmsp_target_id = t.tcmsp_target_id;


# tcmid
use tcmid;

SELECT count(*) FROM tcmid.herb_ingredient_pairs;
SELECT count(distinct(herb_id)) FROM tcmid.herb_ingredient_pairs;
SELECT count(distinct(ingredients_id)) FROM tcmid.herb_ingredient_pairs;
SELECT count(*) FROM tcmid.herb_info;
SELECT count(distinct(`Gene name`)) FROM tcmid.ingredient_targets_disease_drug;
SELECT count(distinct(`Omim ID`)) FROM tcmid.ingredient_targets_disease_drug;
SELECT count(distinct(tcmid_smiles)) FROM tcmid.ingre_new;
SELECT count(distinct(`Ingredient id`)) FROM tcmid.ingredient_targets_disease_drug;
SELECT count(*) FROM tcmid.ingredient_targets_disease_drug;

SELECT * FROM herb_info_detail as h_detail,
herb_info as h,
stitch_annotation as m,
admet_prediction as m_ad,
herb_ingredient_pairs as h_m
where h.`Chinese Name` = '紫草'
and h.`Pinyin Name`= h_detail.`Pinyin Name`
and h_m.herb_id = h.`herb-id`
and h_m.Ingredients_id = m.`Ingredient id`
and m.SMILES = m_ad.smiles
;


SELECT * FROM stitch_annotation as m,
stitch_interaction_all as m_t
where m.`Ingredient id` = '9232' 
and m.Stitch_cid_m = m_t.stitch_id;


## tcm-mesh
use tcm_mesh;
SELECT count(*) FROM tcm_mesh.herb_ingredients;
SELECT count(distinct(herb)) FROM tcm_mesh.herb_ingredients;
SELECT count(distinct(chemical)) FROM tcm_mesh.herb_ingredients;

SELECT count(*) FROM tcm_mesh.tcm_chemical_protein_associations;
SELECT count(distinct(protein)) FROM tcm_mesh.tcm_chemical_protein_associations;
SELECT count(distinct(chemical)) FROM tcm_mesh.tcm_chemical_protein_associations;


SELECT count(*) FROM tcm_mesh.side_effect;
SELECT count(distinct(chemical)) FROM tcm_mesh.side_effect;
SELECT count(distinct(side_effect)) FROM tcm_mesh.side_effect;

SELECT count(*) FROM tcm_mesh.chemical_protein_associations;
SELECT count(distinct(chemical)) FROM tcm_mesh.chemical_protein_associations;
SELECT count(distinct(protein)) FROM tcm_mesh.chemical_protein_associations;

SELECT count(distinct(chemical)) FROM tcm_mesh.chemical_protein_associations where `combined score` >= 700;
create table herb_ingre_tar SELECT cp.*
FROM tcm_mesh.chemical_protein_associations as cp,
tcm_mesh.herb_ingredients as c where
cp.chemical = c.chemical;

SELECT count(*) FROM tcm_mesh.toxicity;
SELECT count(distinct(name)) FROM tcm_mesh.toxicity;
SELECT count(distinct(toxicity)) FROM tcm_mesh.toxicity;

create table compounds as SELECT t.chemical, t.`CAN string`, t.name FROM tcm_mesh.chemical_protein_associations as t group by chemical;


SELECT * FROM herb_info as h,
            herb_ingredients as h_m,
            compounds as m
            where h.`pinyin name` = 'A WEI'
            and h.`pinyin name` = h_m.herb
            and m.chemical = h_m.chemical;
            


SELECT * FROM compounds as m,
            protein_gene_links as t,
            chemical_protein_associations as m_t
            where m.chemical = 'CID000005815'
            and m_t.chemical = m.chemical
            and m_t.protein = t.protein;


SELECT * FROM 
            chemical_protein_associations as m_t
            where m_t.chemical = 'CID000005815';
		
SELECT * FROM 
	tcm_mesh.side_effect as side
	where side.chemical = 'CID000005815';
            
SELECT * FROM 
            tcm_mesh.toxicity as toxi
            where toxi.chemical  = 'CID000005815';
            
## ETCM

SELECT count(*) FROM etcm.herb_ingredient;
SELECT count(distinct(herb_id)) FROM etcm.herb_ingredient;
SELECT count(distinct(ingre_id)) FROM etcm.herb_ingredient;

SELECT count(*) FROM etcm.ingredient_target;
SELECT count(distinct(target)) FROM etcm.ingredient_target;
SELECT count(distinct(ingre_id)) FROM etcm.ingredient_target;

use etcm;
SELECT * FROM herb_info as h,
            herb_ingredient_target as h_m,
            ingredient_info as m
            where h.herb_id = h_m.herb_id
            and m.Ingredient_id = h_m.ingre_id;

## symmap
SELECT count(*) FROM symmap.smit where Molecule_formula IS NOT NULL AND
NOT Molecule_formula = ' ';

SELECT count(distinct(Herb_id)) FROM symmap.smhb_smit;

SELECT count(*) FROM symmap.smit_smtt;
SELECT count(distinct(MOL_id)) FROM symmap.smit_smtt;
SELECT count(distinct(Gene_id)) FROM symmap.smit_smtt;


#herb
SELECT count(*) FROM tcm_herb.herb_ingredient_info where Ingredient_Smilecompounds IS NOT NULL;


#TCMIO

SELECT count(*) FROM tcmio.tcm_ingredient_relation;
SELECT count(distinct(tcm_id)) FROM tcmio.tcm_ingredient_relation;
SELECT count(distinct(ingredient_id)) FROM tcmio.tcm_ingredient_relation;

SELECT count(*) FROM tcmio.ingredient_target_relation;
SELECT count(distinct(ingredient_id)) FROM tcmio.ingredient_target_relation;
SELECT count(distinct(target_id)) FROM tcmio.ingredient_target_relation;

SELECT COUNT(*) FROM tcmio.ingredient WHERE smiles is not null ;
