Both drafts below await supervisor confirmation. Paths are relative to the worktree unless absolute. Evidence aliases resolve through each document’s `sources`.

```json
{
  "status": "draft_pending_supervisor_confirmation",
  "sources": {
    "S": {
      "file": "product/nz_election/fixtures/representation-commission/schedule-b.pdf",
      "printed_page": 28,
      "text": "/Users/byron/unattended-captures/m2/representation-commission/schedule-b.txt",
      "locator_convention": "S:L identifies a 1-based line in the supplied text extraction."
    },
    "R": {
      "file": "product/nz_election/fixtures/representation-commission/report-2025.pdf",
      "text": "/Users/byron/unattended-captures/m2/representation-commission/report-2025.txt",
      "locator_convention": "Page numbers are printed report pages; headings and paragraph numbers identify the passage."
    },
    "G": {
      "file": "product/nz_election/fixtures/stats-nz/general-2025.geojson",
      "id_property": "GED2025_V1_00",
      "name_property": "GED2025_V1_00_NAME"
    },
    "M": {
      "file": "product/nz_election/fixtures/stats-nz/maori-2025.geojson",
      "id_property": "MED2025_V1_00",
      "name_property": "MED2025_V1_00_NAME"
    },
    "O": {
      "file": "product/nz_election/fixtures/ec-2023-xml/electorates.xml",
      "locator": "electorate[@e_no=old_id]/electorate_name",
      "name_cross_check": "product/nz_election/fixtures/ec-2023/party-votes.csv, Electorate column"
    }
  },
  "interpretation": {
    "new_ids": "Exact source strings, including general-electorate leading zeroes; Māori IDs remain unpadded.",
    "old_ids": "Continuing predecessor seats and additional contributors expressly named in the report; not an exhaustive polygon-intersection concordance.",
    "relationships": "Explicit same-seat name changes are renamed. The five reconfigured replacement seats are provisionally created; their six replaced predecessors receive abolished records. See ambiguity A1.",
    "notes": "Report sentences or bullet wording, with whitespace normalized and terminal punctuation added where needed.",
    "review_fields": "Requested reviewer and date are proposed attribution, not evidence that supervisor review has occurred.",
    "no_weighting": "No population weights, vote transfers, or authority to sum predecessor election totals."
  },
  "ambiguities": {
    "A1": "The executive summary calls these electorates replaced/reconfigured, but groups all ten new names under Name changes; paragraph 93 also uses renamed broadly. Created/abolished is a provisional translation into the requested taxonomy, requiring supervisor confirmation.",
    "A2": "Schedule B expressly marks Taupō changed, but the supplied report narrative does not identify its specific boundary movement. No locality transfer or donor seat is inferred."
  },
  "totals": {
    "new_general": 64,
    "new_maori": 7,
    "new_total": 71,
    "old_general": 65,
    "old_maori": 7,
    "distinct_old_ids_covered": 72,
    "replacement_predecessor_records": 6,
    "entry_count": 77,
    "new_relationship_counts": {
      "unchanged": 18,
      "boundary_changed": 43,
      "renamed": 5,
      "created": 5
    },
    "unchanged_boundaries_including_renamed_East_Cape": 19
  },
  "entries": [
    {"new_id":"001","new_name":"Auckland Central","old_ids":[1],"old_names":["Auckland Central"],"relationship":"boundary_changed","note":"The boundaries of Auckland Central, Mt Albert and Epsom move in a roughly anticlockwise direction, while Tāmaki and Maungakiekie move eastwards and Mt Roskill moves westwards.","evidence":["S:14","R: Auckland, p19, paragraph 52"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"002","new_name":"Banks Peninsula","old_ids":[2],"old_names":["Banks Peninsula"],"relationship":"unchanged","note":"All these electorates remain unchanged from their 2020 boundaries and names.","evidence":["S:7","R: Elsewhere, p22, paragraph 68"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"003","new_name":"Botany","old_ids":[4,48,38],"old_names":["Botany","Takanini","Papakura"],"relationship":"boundary_changed","note":"Papakura moves southwards and shifts rural population to Botany, which in turn shifts some urban population to Pakuranga.","evidence":["S:16","R: Auckland, p19, paragraph 54, Takanini and Papakura bullets"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"004","new_name":"Christchurch Central","old_ids":[5],"old_names":["Christchurch Central"],"relationship":"boundary_changed","note":"Through the hearings process, we adopted an alternate proposal that kept Redwood within Christchurch Central and instead moved a section in Linwood/Phillipstown between Fitzgerald Avenue, Avonside Drive, and Tuam Street into Christchurch East.","evidence":["S:24","R: Christchurch, p21, paragraph 64"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"005","new_name":"Christchurch East","old_ids":[6,5],"old_names":["Christchurch East","Christchurch Central"],"relationship":"boundary_changed","note":"Through the hearings process, we adopted an alternate proposal that kept Redwood within Christchurch Central and instead moved a section in Linwood/Phillipstown between Fitzgerald Avenue, Avonside Drive, and Tuam Street into Christchurch East.","evidence":["S:24","R: Christchurch, p21, paragraph 64"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"006","new_name":"Coromandel","old_ids":[7],"old_names":["Coromandel"],"relationship":"unchanged","note":"Nineteen electorates are unchanged.","evidence":["S:4","R: Executive summary, p7, opening paragraph"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"007","new_name":"Dunedin","old_ids":[8],"old_names":["Dunedin"],"relationship":"unchanged","note":"All these electorates remain unchanged from their 2020 boundaries and names.","evidence":["S:8","R: Elsewhere, p22, paragraph 68"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"008","new_name":"East Cape","old_ids":[9],"old_names":["East Coast"],"relationship":"renamed","note":"East Coast becomes East Cape.","evidence":["S:5, unchanged boundaries","R: Executive summary / Name changes, p9","R: Naming electorates / Changed names, p25, paragraph 90"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"009","new_name":"East Coast Bays","old_ids":[10,63,55],"old_names":["East Coast Bays","Whangaparāoa","Upper Harbour"],"relationship":"boundary_changed","note":"Upper Harbour, which must lose population, experiences significant changes in addition to those mentioned above, shifting two areas to Henderson and East Coast Bays.","evidence":["S:11","R: Auckland, pp18-19, paragraph 51, Whangaparāoa and Upper Harbour transfers"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"010","new_name":"Epsom","old_ids":[11],"old_names":["Epsom"],"relationship":"boundary_changed","note":"The boundaries of Auckland Central, Mt Albert and Epsom move in a roughly anticlockwise direction, while Tāmaki and Maungakiekie move eastwards and Mt Roskill moves westwards.","evidence":["S:14","R: Auckland, p19, paragraphs 52-53"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"011","new_name":"Glendene","old_ids":[19,53],"old_names":["Kelston","Te Atatū"],"relationship":"created","note":"Parts of Kelston and Te Atatū become Glendene.","evidence":["R: Executive summary / Name changes, p9","R: Auckland, p18, paragraph 50"],"ambiguity":"A1","reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"012","new_name":"Hamilton East","old_ids":[12],"old_names":["Hamilton East"],"relationship":"unchanged","note":"Nineteen electorates are unchanged.","evidence":["S:5","R: Executive summary, p7, opening paragraph"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"013","new_name":"Hamilton West","old_ids":[13],"old_names":["Hamilton West"],"relationship":"unchanged","note":"Nineteen electorates are unchanged.","evidence":["S:5","R: Executive summary, p7, opening paragraph"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"014","new_name":"Henderson","old_ids":[53,55,18],"old_names":["Te Atatū","Upper Harbour","Kaipara ki Mahurangi"],"relationship":"created","note":"Parts of Te Atatū, Upper Harbour and Kaipara ki Mahurangi become Henderson.","evidence":["R: Executive summary / Name changes, p9, Henderson bullet; asterisk denotes a change from the March proposal","R: Auckland, pp18-19, paragraphs 50-51"],"ambiguity":"A1","reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"015","new_name":"Hutt South","old_ids":[14],"old_names":["Hutt South"],"relationship":"boundary_changed","note":"Hutt South and Remutaka both shift south-westwards, with the former taking in eastern Newlands.","evidence":["S:23","R: Lower North Island, p18, paragraph 48"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"016","new_name":"Ilam","old_ids":[15],"old_names":["Ilam"],"relationship":"boundary_changed","note":"This in turn necessitated flow-on changes to Christchurch Central, Christchurch East and Ilam, to ensure they remained within quota.","evidence":["S:24","R: Christchurch, p21, paragraph 61, following the Selwyn-to-Wigram transfer"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"017","new_name":"Invercargill","old_ids":[16,46],"old_names":["Invercargill","Southland"],"relationship":"boundary_changed","note":"Our proposed changes involved a population of around 900 in the vicinity of Nightcaps and Otautau moving from Southland to Invercargill.","evidence":["S:26","R: Southland, p21, paragraphs 66-67, proposed boundaries retained"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"018","new_name":"Kaikōura","old_ids":[17],"old_names":["Kaikōura"],"relationship":"unchanged","note":"The Commission did receive a small number of submissions from West Coast-Tasman and Kaikōura, however we have been unable to accommodate these suggestions due to population quota requirements, and they remain unchanged from 2020 boundaries and names.","evidence":["S:6","R: Elsewhere, p22, paragraph 69"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"019","new_name":"Kaipara ki Mahurangi","old_ids":[18,63],"old_names":["Kaipara ki Mahurangi","Whangaparāoa"],"relationship":"boundary_changed","note":"Kaipara ki Mahurangi shifts population to Upper Harbour and Henderson, while gaining an area from Whangaparāoa, which in turn shifts population to East Coast Bays.","evidence":["S:10","R: Auckland, p18, paragraph 51"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"020","new_name":"Kapiti","old_ids":[34,20],"old_names":["Ōtaki","Mana"],"relationship":"created","note":"Parts of Ōtaki and Mana become Kapiti.","evidence":["R: Executive summary / Name changes, p9","R: Lower North Island, p18, paragraphs 46-47"],"ambiguity":"A1","reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"021","new_name":"Kenepuru","old_ids":[20,33],"old_names":["Mana","Ōhāriu"],"relationship":"created","note":"Parts of Mana and Ōhāriu become Kenepuru.","evidence":["R: Executive summary / Name changes, p9","R: Lower North Island, p18, paragraphs 46-47"],"ambiguity":"A1","reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"022","new_name":"Māngere","old_ids":[21],"old_names":["Māngere"],"relationship":"boundary_changed","note":"There are also changes on the eastern boundaries of both Māngere and Manurewa.","evidence":["S:16","R: Auckland, p19, paragraph 54"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"023","new_name":"Manurewa","old_ids":[22],"old_names":["Manurewa"],"relationship":"boundary_changed","note":"There are also changes on the eastern boundaries of both Māngere and Manurewa.","evidence":["S:17","R: Auckland, p19, paragraph 54"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"024","new_name":"Maungakiekie","old_ids":[23],"old_names":["Maungakiekie"],"relationship":"boundary_changed","note":"The boundaries of Auckland Central, Mt Albert and Epsom move in a roughly anticlockwise direction, while Tāmaki and Maungakiekie move eastwards and Mt Roskill moves westwards.","evidence":["S:15","R: Auckland, p19, paragraphs 52-53"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"025","new_name":"Mt Albert","old_ids":[24,1],"old_names":["Mt Albert","Auckland Central"],"relationship":"boundary_changed","note":"To ensure Mt Albert remains within quota, an area around Arch Hill is shifted from Auckland Central to Mt Albert.","evidence":["S:14","R: Auckland, p19, paragraph 53"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"026","new_name":"Mt Maunganui","old_ids":[3,52],"old_names":["Bay of Plenty","Tauranga"],"relationship":"renamed","note":"Parts of Bay of Plenty and Tauranga become Mt Maunganui.","evidence":["R: Executive summary / Name changes, p9","R: Bay of Plenty, p20, paragraphs 56-57, explicitly renames Bay of Plenty"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"027","new_name":"Mt Roskill","old_ids":[25],"old_names":["Mt Roskill"],"relationship":"boundary_changed","note":"The boundaries of Auckland Central, Mt Albert and Epsom move in a roughly anticlockwise direction, while Tāmaki and Maungakiekie move eastwards and Mt Roskill moves westwards.","evidence":["S:13","R: Auckland, p19, paragraph 52"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"028","new_name":"Napier","old_ids":[26,54],"old_names":["Napier","Tukituki"],"relationship":"boundary_changed","note":"Instead, Napier gains a rural area from Tukituki north of the Ngaruroro River.","evidence":["S:20","R: Executive summary / North Island general electorates, p8","R: Central North Island, p20, paragraph 58"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"029","new_name":"Nelson","old_ids":[27],"old_names":["Nelson"],"relationship":"unchanged","note":"All these electorates remain unchanged from their 2020 boundaries and names.","evidence":["S:6","R: Elsewhere, p22, paragraph 68"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"030","new_name":"New Plymouth","old_ids":[29,50],"old_names":["New Plymouth","Taranaki-King Country"],"relationship":"boundary_changed","note":"New Plymouth gains a small area east of the Waitara River from Taranaki-King Country, so Waitara township is now wholly within New Plymouth instead of being split between the two electorates.","evidence":["S:19","R: Central North Island, p20, paragraph 58"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"031","new_name":"North Shore","old_ids":[30,10],"old_names":["North Shore","East Coast Bays"],"relationship":"boundary_changed","note":"East Coast Bays also shifts small areas to both Upper Harbour and North Shore.","evidence":["S:11","R: Auckland, p18, paragraph 51"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"032","new_name":"Northcote","old_ids":[31],"old_names":["Northcote"],"relationship":"boundary_changed","note":"Northcote and North Shore both expand northward in small areas, while Kaipara ki Mahurangi expands into a small area south of Coatesville, which is moved from Whangaparāoa.","evidence":["S:12","R: Executive summary / North Island general electorates, p7"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"033","new_name":"Northland","old_ids":[32],"old_names":["Northland"],"relationship":"boundary_changed","note":"Due to Northland being over quota we proposed moving a rural area between Whangaruru Harbour and Whananaki from Northland to Whangārei.","evidence":["S:10","R: North of Auckland, p20, paragraph 55, proposed changes adopted without amendment"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"034","new_name":"Ōtāhuhu","old_ids":[37,4,48],"old_names":["Panmure-Ōtāhuhu","Botany","Takanini"],"relationship":"renamed","note":"There are relatively significant changes to Ōtāhuhu, which shifts south-eastwards and is renamed from Panmure-Ōtāhuhu.","evidence":["R: Executive summary / Name changes, p9, Panmure-Ōtāhuhu and Botany predecessors","R: Auckland, p19, paragraph 54, explicit rename and Takanini transfer"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"035","new_name":"Pakuranga","old_ids":[35,4],"old_names":["Pakuranga","Botany"],"relationship":"boundary_changed","note":"Papakura moves southwards and shifts rural population to Botany, which in turn shifts some urban population to Pakuranga.","evidence":["S:15","R: Auckland, p19, paragraph 54"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"036","new_name":"Palmerston North","old_ids":[36],"old_names":["Palmerston North"],"relationship":"boundary_changed","note":"Palmerston North expands around the city including the township of Bunnythorpe.","evidence":["S:21","R: Central North Island, p20, paragraph 58"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"037","new_name":"Papakura","old_ids":[38,48],"old_names":["Papakura","Takanini"],"relationship":"boundary_changed","note":"Papakura moves southwards and shifts rural population to Botany, which in turn shifts some urban population to Pakuranga.","evidence":["S:17","R: Auckland, p19, paragraph 54, Takanini and Papakura bullets"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"038","new_name":"Port Waikato","old_ids":[39],"old_names":["Port Waikato"],"relationship":"unchanged","note":"Nineteen electorates are unchanged.","evidence":["S:4","R: Executive summary, p7, opening paragraph"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"039","new_name":"Rangitata","old_ids":[40],"old_names":["Rangitata"],"relationship":"unchanged","note":"All these electorates remain unchanged from their 2020 boundaries and names.","evidence":["S:7","R: Elsewhere, p22, paragraphs 68 and 70"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"040","new_name":"Rangitīkei","old_ids":[41],"old_names":["Rangitīkei"],"relationship":"boundary_changed","note":"Rangitīkei extends southwards to include Foxton, Levin and Manakau.","evidence":["S:21","R: Executive summary / North Island general electorates, p8"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"041","new_name":"Remutaka","old_ids":[42],"old_names":["Remutaka"],"relationship":"boundary_changed","note":"Hutt South and Remutaka both shift south-westwards, with the former taking in eastern Newlands.","evidence":["S:22","R: Lower North Island, p18, paragraph 48"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"042","new_name":"Rotorua","old_ids":[44],"old_names":["Rotorua"],"relationship":"boundary_changed","note":"Tauranga expands westward to the boundary with Coromandel; Bay of Plenty, which is renamed Mt Maunganui, gains the town centre and natural feature of the same name; and Rotorua expands northwards as far as the southern outskirts of Tauranga city.","evidence":["S:18","R: Bay of Plenty, p20, paragraphs 56-57"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"043","new_name":"Selwyn","old_ids":[45],"old_names":["Selwyn"],"relationship":"boundary_changed","note":"Due to rapid growth in Selwyn, which was originally 14% over quota, we proposed moving the communities of Prebbleton and Templeton and their surrounding areas from Selwyn into Wigram.","evidence":["S:25","R: Christchurch, p21, paragraphs 61-62, transfer retained"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"044","new_name":"Southland","old_ids":[46],"old_names":["Southland"],"relationship":"boundary_changed","note":"Our proposed changes involved a population of around 900 in the vicinity of Nightcaps and Otautau moving from Southland to Invercargill.","evidence":["S:25","R: Southland, p21, paragraphs 66-67, proposed boundaries retained"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"045","new_name":"Taieri","old_ids":[47],"old_names":["Taieri"],"relationship":"unchanged","note":"All these electorates remain unchanged from their 2020 boundaries and names.","evidence":["S:8","R: Elsewhere, p22, paragraph 68"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"046","new_name":"Takanini","old_ids":[48],"old_names":["Takanini"],"relationship":"boundary_changed","note":"Substantial population is shifted from this electorate to Botany, Papakura and Ōtāhuhu.","evidence":["S:17","R: Auckland, p19, paragraph 54, Takanini bullet"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"047","new_name":"Tāmaki","old_ids":[49],"old_names":["Tāmaki"],"relationship":"boundary_changed","note":"The boundaries of Auckland Central, Mt Albert and Epsom move in a roughly anticlockwise direction, while Tāmaki and Maungakiekie move eastwards and Mt Roskill moves westwards.","evidence":["S:15","R: Auckland, p19, paragraph 52"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"048","new_name":"Taranaki-King Country","old_ids":[50],"old_names":["Taranaki-King Country"],"relationship":"boundary_changed","note":"Taranaki-King Country gains Taumarunui.","evidence":["S:19","R: Central North Island, p20, paragraph 58"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"049","new_name":"Taupō","old_ids":[51],"old_names":["Taupō"],"relationship":"boundary_changed","note":"The boundaries of 49 general and three Māori electorates have been adjusted.","evidence":["S:19","R: Executive summary, p7"],"ambiguity":"A2","reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"050","new_name":"Tauranga","old_ids":[52],"old_names":["Tauranga"],"relationship":"boundary_changed","note":"Tauranga expands westward to the boundary with Coromandel; Bay of Plenty, which is renamed Mt Maunganui, gains the town centre and natural feature of the same name; and Rotorua expands northwards as far as the southern outskirts of Tauranga city.","evidence":["S:18","R: Bay of Plenty, p20, paragraphs 56-57"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"051","new_name":"Tukituki","old_ids":[54],"old_names":["Tukituki"],"relationship":"boundary_changed","note":"Instead, Napier gains a rural area from Tukituki north of the Ngaruroro River.","evidence":["S:20","R: Executive summary / North Island general electorates, p8","R: Central North Island, p20, paragraph 58"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"052","new_name":"Upper Harbour","old_ids":[55,18,10],"old_names":["Upper Harbour","Kaipara ki Mahurangi","East Coast Bays"],"relationship":"boundary_changed","note":"East Coast Bays also shifts small areas to both Upper Harbour and North Shore.","evidence":["S:12","R: Auckland, pp18-19, paragraph 51, Kaipara ki Mahurangi and East Coast Bays transfers"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"053","new_name":"Waikato","old_ids":[56],"old_names":["Waikato"],"relationship":"unchanged","note":"Nineteen electorates are unchanged.","evidence":["S:4","R: Executive summary, p7, opening paragraph"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"054","new_name":"Waimakariri","old_ids":[57],"old_names":["Waimakariri"],"relationship":"unchanged","note":"All these electorates remain unchanged from their 2020 boundaries and names.","evidence":["S:7","R: Elsewhere, p22, paragraph 68"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"055","new_name":"Wairarapa","old_ids":[58],"old_names":["Wairarapa"],"relationship":"boundary_changed","note":"Wairarapa incorporates Ashhurst.","evidence":["S:21","R: Central North Island, p20, paragraphs 58-59"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"056","new_name":"Waitākere","old_ids":[28,19],"old_names":["New Lynn","Kelston"],"relationship":"created","note":"New Lynn and parts of Kelston become Waitākere.","evidence":["R: Executive summary / Name changes, p9","R: Auckland, p18, paragraph 50"],"ambiguity":"A1","reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"057","new_name":"Waitaki","old_ids":[59],"old_names":["Waitaki"],"relationship":"unchanged","note":"All these electorates remain unchanged from their 2020 boundaries and names.","evidence":["S:8","R: Elsewhere, p22, paragraphs 68 and 70"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"058","new_name":"Wellington Bays","old_ids":[43],"old_names":["Rongotai"],"relationship":"renamed","note":"Rongotai becomes Wellington Bays.","evidence":["R: Executive summary / Name changes, p9","R: Lower North Island, p18, paragraph 49","R: Naming electorates / Changed names, p25, paragraph 90"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"059","new_name":"Wellington North","old_ids":[60],"old_names":["Wellington Central"],"relationship":"renamed","note":"Wellington Central becomes Wellington North.","evidence":["R: Executive summary / Name changes, p9","R: Lower North Island, p18, paragraph 49","R: Naming electorates / Changed names, p25, paragraph 90"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"060","new_name":"West Coast-Tasman","old_ids":[61],"old_names":["West Coast-Tasman"],"relationship":"unchanged","note":"The Commission did receive a small number of submissions from West Coast-Tasman and Kaikōura, however we have been unable to accommodate these suggestions due to population quota requirements, and they remain unchanged from 2020 boundaries and names.","evidence":["S:6","R: Elsewhere, p22, paragraph 69"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"061","new_name":"Whanganui","old_ids":[62],"old_names":["Whanganui"],"relationship":"boundary_changed","note":"Whanganui extends north and north-eastwards incorporating Ōwhango and Waiouru.","evidence":["S:20","R: Central North Island, p20, paragraph 58"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"062","new_name":"Whangaparāoa","old_ids":[63],"old_names":["Whangaparāoa"],"relationship":"boundary_changed","note":"Kaipara ki Mahurangi shifts population to Upper Harbour and Henderson, while gaining an area from Whangaparāoa, which in turn shifts population to East Coast Bays.","evidence":["S:11","R: Auckland, pp18-19, paragraph 51"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"063","new_name":"Whangārei","old_ids":[64,32],"old_names":["Whangārei","Northland"],"relationship":"boundary_changed","note":"Due to Northland being over quota we proposed moving a rural area between Whangaruru Harbour and Whananaki from Northland to Whangārei.","evidence":["S:10","R: North of Auckland, p20, paragraph 55, proposed changes adopted without amendment"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"064","new_name":"Wigram","old_ids":[65,45],"old_names":["Wigram","Selwyn"],"relationship":"boundary_changed","note":"Due to rapid growth in Selwyn, which was originally 14% over quota, we proposed moving the communities of Prebbleton and Templeton and their surrounding areas from Selwyn into Wigram.","evidence":["S:25","R: Christchurch, p21, paragraphs 61-62, transfer retained"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"1","new_name":"Hauraki-Waikato","old_ids":[66],"old_names":["Hauraki-Waikato"],"relationship":"unchanged","note":"Nineteen electorates are unchanged.","evidence":["S:28","R: Executive summary, p7, opening paragraph"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"2","new_name":"Ikaroa-Rāwhiti","old_ids":[67,71],"old_names":["Ikaroa-Rāwhiti","Te Tai Tonga"],"relationship":"boundary_changed","note":"Ikaroa-Rāwhiti gains an area in Lower Hutt and its eastern bays area from Te Tai Tonga.","evidence":["S:31","R: Executive summary / Māori electorates, p8","R: Māori electorates, p23, paragraphs 74-75"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"3","new_name":"Tāmaki Makaurau","old_ids":[68],"old_names":["Tāmaki Makaurau"],"relationship":"unchanged","note":"Accordingly, no changes have been made to this electorate as it remains within the required population quota.","evidence":["S:28","R: Māori electorates, p23, paragraph 76"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"4","new_name":"Te Tai Hauāuru","old_ids":[69],"old_names":["Te Tai Hauāuru"],"relationship":"boundary_changed","note":"The boundary between Te Tai Tonga and Te Tai Hauāuru has a minor adjustment in Horokiwi, affecting no population.","evidence":["S:31","R: Executive summary / Māori electorates, p8"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"5","new_name":"Te Tai Tokerau","old_ids":[70],"old_names":["Te Tai Tokerau"],"relationship":"unchanged","note":"Nineteen electorates are unchanged.","evidence":["S:28","R: Executive summary, p7, opening paragraph"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"6","new_name":"Te Tai Tonga","old_ids":[71],"old_names":["Te Tai Tonga"],"relationship":"boundary_changed","note":"Ikaroa-Rāwhiti gains an area in Lower Hutt and its eastern bays area from Te Tai Tonga.","evidence":["S:31","R: Executive summary / Māori electorates, p8, also records the Horokiwi adjustment","R: Māori electorates, p23, paragraphs 74-75"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":"7","new_name":"Waiariki","old_ids":[72],"old_names":["Waiariki"],"relationship":"unchanged","note":"Nineteen electorates are unchanged.","evidence":["S:29","R: Executive summary, p7, opening paragraph"],"reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":null,"new_name":null,"old_ids":[19],"old_names":["Kelston"],"relationship":"abolished","note":"In western Auckland three electorates - New Lynn, Kelston and Te Atatū - are replaced by reconfigured electorates: Waitākere, Glendene and Henderson.","evidence":["R: Executive summary / North Island general electorates, p7","R: Executive summary / Name changes, p9"],"ambiguity":"A1","reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":null,"new_name":null,"old_ids":[28],"old_names":["New Lynn"],"relationship":"abolished","note":"In western Auckland three electorates - New Lynn, Kelston and Te Atatū - are replaced by reconfigured electorates: Waitākere, Glendene and Henderson.","evidence":["R: Executive summary / North Island general electorates, p7","R: Executive summary / Name changes, p9"],"ambiguity":"A1","reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":null,"new_name":null,"old_ids":[53],"old_names":["Te Atatū"],"relationship":"abolished","note":"In western Auckland three electorates - New Lynn, Kelston and Te Atatū - are replaced by reconfigured electorates: Waitākere, Glendene and Henderson.","evidence":["R: Executive summary / North Island general electorates, p7","R: Executive summary / Name changes, p9"],"ambiguity":"A1","reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":null,"new_name":null,"old_ids":[20],"old_names":["Mana"],"relationship":"abolished","note":"Three lower North Island electorates, Ōtaki, Mana and Ōhāriu, are reconfigured as two electorates, Kapiti and Kenepuru.","evidence":["R: Executive summary / North Island general electorates, p8","R: Lower North Island, p18, paragraph 46"],"ambiguity":"A1","reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":null,"new_name":null,"old_ids":[33],"old_names":["Ōhāriu"],"relationship":"abolished","note":"Three lower North Island electorates, Ōtaki, Mana and Ōhāriu, are reconfigured as two electorates, Kapiti and Kenepuru.","evidence":["R: Executive summary / North Island general electorates, p8","R: Lower North Island, p18, paragraph 46"],"ambiguity":"A1","reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"},
    {"new_id":null,"new_name":null,"old_ids":[34],"old_names":["Ōtaki"],"relationship":"abolished","note":"Three lower North Island electorates, Ōtaki, Mana and Ōhāriu, are reconfigured as two electorates, Kapiti and Kenepuru.","evidence":["R: Executive summary / North Island general electorates, p8","R: Lower North Island, p18, paragraph 46"],"ambiguity":"A1","reviewer":"supervisor (Claude), unattended lab","review_date":"2026-10-17"}
  ]
}
```

```json
{
  "status": "draft_pending_supervisor_confirmation",
  "sources": {
    "identity_root": "product/nz_election/fixtures/party-identity/",
    "M1": "product/nz_election/config/party-colours.json",
    "M1_usage": "product/nz_election/pipeline/build.py:103 loads party-colours; line 116 reads each party's colour",
    "capture_manifest": "product/nz_election/fixtures/manifest.json"
  },
  "locator_convention": "Lines are 1-based; byte offsets are 0-based offsets in the original captured bytes.",
  "inspection": {
    "meta_theme_color": "Absent from all seven captures.",
    "preference_order": [
      "meta theme-color",
      "CSS custom-property declarations",
      "inline styles",
      "class names containing a hex value"
    ],
    "additional_evidence": "Embedded stylesheet rules and inline SVG presentation attributes are identified separately.",
    "visible_identity_evidence": "Means literal colours attached to page UI in the HTML, not a rendered-page or official brand-manual verification.",
    "reviewer": "supervisor (Claude), unattended lab",
    "review_date": "2026-10-17",
    "review_status": "Unconfirmed"
  },
  "parties": {
    "nat": {
      "label": "National",
      "file": "nat.html",
      "recommended_primary": null,
      "reason": "Primary blue appears through semantic classes whose colour definitions are external. The literal colours found are pale surfaces, border fallbacks and black overlays, insufficient to identify the primary blue.",
      "candidates": [
        {
          "colour": "#F8FAFC",
          "kind": "CSS custom property and inline style",
          "locator": "line 1, byte 33457: div.text-blue-dark style=\"background-color:#f8fafc;--section-bg:#f8fafc\"",
          "role": "Section surface; reject as primary."
        },
        {
          "colour": "#FFFFFF",
          "kind": "CSS custom property and inline style",
          "locator": "line 2: div.text-blue-dark style=\"background-color:#ffffff;--section-bg:#ffffff\"",
          "role": "Section surface; reject as primary."
        },
        {
          "colour": "#E9F2FC",
          "kind": "Class containing hex",
          "locator": "line 1, byte 33954: a[href='/connect'] class contains border-[var(--section-bg,#E9F2FC)]",
          "role": "Border fallback; not necessarily the rendered colour and not primary-blue evidence."
        }
      ],
      "html_identity_evidence": "Partial: visible surfaces have literal values, but primary blue requires external CSS.",
      "external_css_needed": [
        "https://www.national.org.nz/_next/static/immutable/chunks/12i8kach4_2p3.css",
        "https://www.national.org.nz/_next/static/immutable/chunks/2f9wyvxctmtoc.css"
      ],
      "external_css_locator": "line 1, stylesheet href filenames at bytes 1141 and 1244; inspect definitions for text-blue-dark and bg-blue classes",
      "m1_colour": "#00529F",
      "m1_locator": "M1:2, nat.colour",
      "comparison": "unverified",
      "comparison_reason": "Neither agree nor differ can be established for primary blue from this HTML."
    },
    "lab": {
      "label": "Labour",
      "file": "lab.html",
      "recommended_primary": "#D82C20",
      "reason": "Repeated navigation colour, explicitly assigned to a link custom property and to the mobile menu background.",
      "candidates": [
        {
          "colour": "#D82C20",
          "kind": "CSS custom property and inline style",
          "locator": "line 462, byte 21156: a.nav-header-item style includes color:#d82c20;--block-link-colour:#d82c20",
          "corroboration": "line 267: embedded .burger-menu-container { background-color:#d82c20!important; }"
        },
        {
          "colour": "#E2261E",
          "kind": "Inline style",
          "locator": "line 536: #Buttonf1f78b50-388c-437b-92b0-ac7d105f0089 background-color",
          "role": "Button red variant."
        },
        {
          "colour": "#A42A2E",
          "kind": "Inline style",
          "locator": "line 977: button style border-color",
          "role": "Border red variant."
        },
        {
          "colour": "#E53641",
          "kind": "Embedded stylesheet",
          "locator": "line 488: #HeaderLinks1ed0f380-b6e5-4342-ab06-af1206d0cfd9 .link-style:hover",
          "role": "Hover red variant."
        }
      ],
      "html_identity_evidence": "Yes: navigation links and menu styling contain literal red values.",
      "external_css_needed": [],
      "m1_colour": "#D82C20",
      "m1_locator": "M1:3, lab.colour",
      "comparison": "agree"
    },
    "grn": {
      "label": "Green",
      "file": "grn.html",
      "recommended_primary": "#00491E",
      "reason": "Literal dark green appears on the party's About us link and recurring navigation graphics.",
      "candidates": [
        {
          "colour": "#00491E",
          "kind": "Inline style",
          "locator": "line 2717: a[href='/about'] style color:#00491e",
          "corroboration": "line 1005: inline SVG circle fill=\"#00491E\"; line 5583: navigation SVG path stroke=\"#00491e\""
        },
        {
          "colour": "#ECF5E9",
          "kind": "Inline style",
          "locator": "line 7454: full-width div style background-color:#ecf5e9!important",
          "role": "Pale green section background."
        },
        {
          "colour": "#F9F9F1",
          "kind": "Inline style",
          "locator": "line 6822: div style border:1px solid #F9F9F1!important",
          "role": "Light supporting neutral."
        }
      ],
      "html_identity_evidence": "Yes: party navigation and page content carry explicit dark green.",
      "external_css_needed": [],
      "m1_colour": "#098137",
      "m1_locator": "M1:4, grn.colour",
      "comparison": "differ",
      "limitation": "The HTML supports this site colour but does not designate an official primary brand swatch."
    },
    "act": {
      "label": "ACT",
      "file": "act.html",
      "recommended_primary": "#EE2796",
      "reason": "Pink is a declared body token used by prominent heading text and the Donate button; yellow and cyan remain evidenced alternatives. The primary choice is an editorial recommendation.",
      "candidates": [
        {
          "colour": "#EE2796",
          "kind": "CSS custom property",
          "locator": "line 266, byte 27710: body --token-6e18aaf2-8eb0-45ff-964a-eabf17cf2aa2:#ee2796",
          "corroboration": "line 281: a[href='https://action.act.org.nz/donate'] descendant div[data-framer-name='Content Filled'] inline background-color uses this token with rgb(238,39,150) fallback"
        },
        {
          "colour": "#FFDF00",
          "kind": "CSS custom property",
          "locator": "line 266, byte 27763: body --token-416d84ec-eb88-4cd4-8062-7f812cddbba8:#ffdf00",
          "role": "Evidenced yellow brand candidate; also used by a Content Filled element on line 281."
        },
        {
          "colour": "#00AEEF",
          "kind": "CSS custom property",
          "locator": "line 266, byte 27816: body --token-85f9e7ee-be17-4a55-96ca-ed5012ff6d3b:#00aeef",
          "role": "Evidenced cyan brand candidate."
        },
        {
          "colour": "#ED0082",
          "kind": "Inline style",
          "locator": "line 281: div.framer-yjvus9[data-framer-name='Desktop'] background linear-gradient starts at rgb(237,0,130)",
          "role": "Pink gradient endpoint; not the main pink token."
        }
      ],
      "html_identity_evidence": "Yes: embedded token declarations and inline component colours.",
      "external_css_needed": [],
      "m1_colour": "#FDE401",
      "m1_locator": "M1:5, act.colour",
      "comparison": "differ",
      "limitation": "No explicit primary-colour designation. Choosing the evidenced yellow instead would still differ from M1: #FFDF00 versus #FDE401."
    },
    "nzf": {
      "label": "NZ First",
      "file": "nzf.html",
      "recommended_primary": null,
      "reason": "No literal party colour was found in the requested HTML evidence forms. A primary colour cannot be sampled from semantic classes or external image references.",
      "candidates": [],
      "html_identity_evidence": "No literal primary-colour evidence; identity styling references external CSS.",
      "external_css_needed": [
        "https://nzfirst.nationbuilder.com/themes/1064/6747a296cf7dc31268999992/0/attachments/17327480131791245274/default/theme.scss"
      ],
      "external_css_locator": "line 66: link[rel='stylesheet'] href",
      "m1_colour": "#000000",
      "m1_locator": "M1:6, nzf.colour",
      "comparison": "unverified",
      "comparison_reason": "Neither agree nor differ can be established without the stylesheet."
    },
    "tpm": {
      "label": "Te Pāti Māori",
      "file": "tpm.html",
      "recommended_primary": "#D12C38",
      "reason": "Explicit red is applied to the party's own Follow Te Pāti Māori social links. This is direct visible-page evidence, although weaker than a declared primary token.",
      "candidates": [
        {
          "colour": "#D12C38",
          "kind": "Inline SVG presentation attribute",
          "locator": "line 7287, byte 143228: svg.homepage-social-media-buttons fill=\"#D12C38\" inside a[href='https://www.facebook.com/MaoriParty']",
          "role": "Party social-link red."
        }
      ],
      "excluded_values": "White search-icon strokes, grey metadata icons and Instagram embed colours do not establish party identity.",
      "html_identity_evidence": "Yes, limited to explicitly coloured party social-link graphics.",
      "external_css_needed": [],
      "optional_primary_confirmation_css": "https://maoriparty.nationbuilder.com/themes/2006/64eeb7f9c18c0209fd2e49a5/0/attachments/16933663571792104757/default/theme.scss",
      "m1_colour": "#B2001A",
      "m1_locator": "M1:7, tpm.colour",
      "comparison": "differ",
      "limitation": "Provisional primary recommendation; the HTML does not label this value as the official primary red."
    },
    "opp": {
      "label": "Opportunity",
      "file": "opp.html",
      "recommended_primary": "#00B9BC",
      "reason": "Teal is explicitly present in a homepage graphic, while the prominent header uses a variable named --brand-teal. The recommendation is provisional because the HTML does not define that variable's value.",
      "candidates": [
        {
          "colour": null,
          "kind": "CSS custom-property reference, not declaration",
          "locator": "lines 594 and 596: .site-header__inner and a[href='/bottom_lines'] inline background:var(--brand-teal)",
          "role": "Strong evidence of a teal brand role, but no literal value."
        },
        {
          "colour": "#00B9BC",
          "kind": "Inline SVG presentation attribute",
          "locator": "line 42157, byte 157282: .homepage-media-mentions__bg svg path fill=\"#00B9BC\" fill-opacity=\"0.35\"",
          "role": "Teal source colour; opacity means the displayed composite is not necessarily this hex."
        },
        {
          "colour": "#443A84",
          "kind": "Inline SVG presentation attribute",
          "locator": "line 730: video-play SVG ellipse fill=\"#443A84\"",
          "role": "Purple alternative, evidenced in a play control."
        },
        {
          "colour": "#B455FF",
          "kind": "Inline SVG presentation attribute",
          "locator": "line 732: video-play SVG path stroke=\"#B455FF\" stroke-opacity=\"0.3\"",
          "role": "Secondary purple stroke."
        }
      ],
      "html_identity_evidence": "Yes, but literal teal is a translucent graphic; the primary header token remains unresolved.",
      "external_css_needed": [
        "https://theopportunitiesparty.nationbuilder.com/themes/3/6912cff4463e166cf162afc7/0/attachments/17677723181792055104/default/site-global.css",
        "https://theopportunitiesparty.nationbuilder.com/themes/3/6912cff4463e166cf162afc7/0/attachments/17677723181792055104/default/site-homepage.css"
      ],
      "external_css_locator": "stylesheet links on lines 47 and 63; inspect --brand-teal declaration and homepage colour rules",
      "m1_colour": "#6B3FA0",
      "m1_locator": "M1:8, opp.colour",
      "comparison": "differ",
      "limitation": "Do not claim that --brand-teal equals #00B9BC until its declaration is captured."
    }
  }
}
```

- **Correspondence ambiguity:** confirm the five `created` and six `abolished` classifications. Their predecessor links are explicit; the report’s terminology does not cleanly match the requested enum. Taupō’s changed status is explicit, but its particular movement is not described.
- **Colour ambiguity:** National and NZ First remain unverified. ACT’s primary choice is editorial; TPM and Opportunity recommendations have limited evidence. Opportunity’s header teal still needs its CSS declaration.
- **Readability:** all requested sources were readable. External stylesheets were not captured or read. No files changed.
- **Verification:** read-only `python3 -B -c` checks produced `PASS manifest hashes: 23`, `PASS correspondence coverage: 71 new seats (64 general, 7 Māori); 72 distinct old EC IDs covered; 6 replaced-seat records; 77 total records.` and `PASS all 72 EC XML names also occur in party-votes.csv.` Used system Python after `uv run --no-project --no-cache` failed because the sandbox prohibited temporary-directory creation.