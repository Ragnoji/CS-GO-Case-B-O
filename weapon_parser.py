import re
import time


def new_weapons(current_items: list[str], old_items: list[str], current_names: list[str]) -> dict:
    # current_items = open('current_items.txt', 'r', encoding='utf-8').readlines()
    # old_items = open('old_items.txt', 'r', encoding='utf-8').readlines()
    # current_names = open('current_names.txt', 'r', encoding='utf-8').readlines()

    new_items = dict()
    ti = time.time()
    for num, line in enumerate(current_items):
        s = re.search('"\[.+\]weapon_[a-z|A-Z|0-9|-|_]+"', line.strip())
        if s is not None and line not in old_items and s[0] not in new_items.keys():
            while True:
                num -= 1
                if num == -1:
                    break
                rarity = re.search('"set_[A-Z|a-z|0-9|_|-]+"', current_items[num].strip())
                if rarity is None:
                    rarity = re.search('"crate_[A-Z|a-z|0-9|_|-]+"', current_items[num].strip())
                if rarity is not None:
                    rarities = {'ancient': 'Covert', 'legendary': 'Classified', 'mythical': 'Restricted',
                                'rare': 'Mil-Spec', 'uncommon': 'Industrial', 'common': 'Consumer',
                                }
                    rarity = rarity[0]
                    collection = rarity[1:rarity.rfind('_')]
                    pointer = '"CSGO_' + collection + '"'
                    for li in current_names:
                        if pointer in li:
                            li = li[:li.rfind('"')]
                            collection = li[li.rfind('"') + 1:]

                    rarity = rarity[rarity.rfind('_') + 1:-1]
                    new_items[s[0]] = (rarities[rarity], collection)
                    break

    parsed_names = {}

    weapon_types = {
        '"weapon_deagle_prefab"': "Desert Eagle",
        '"weapon_elite_prefab"': "Dual Berettas",
        '"weapon_fiveseven_prefab"': "Five-SeveN",
        '"weapon_glock_prefab"': "Glock-18",
        '"weapon_hkp2000_prefab"': "P2000",
        '"weapon_p250_prefab"': "P250",
        '"weapon_cz75a_prefab"': "CZ75-Auto",
        '"weapon_tec9_prefab"': "Tec-9",
        '"weapon_bizon_prefab"': "PP-Bizon",
        '"weapon_mac10_prefab"': "MAC-10",
        '"weapon_mp7_prefab"': "MP7",
        '"weapon_mp5sd_prefab"': "MP5-SD",
        '"weapon_mp9_prefab"': "MP9",
        '"weapon_p90_prefab"': "P90",
        '"weapon_ump45_prefab"': "UMP-45",
        '"weapon_ak47_prefab"': "AK-47",
        '"weapon_aug_prefab"': "AUG",
        '"weapon_famas_prefab"': "FAMAS",
        '"weapon_galilar_prefab"': "Galil AR",
        '"weapon_m4a1_prefab"': "M4A4",
        '"weapon_sg556_prefab"': "SG 553",
        '"weapon_awp_prefab"': "AWP",
        '"weapon_g3sg1_prefab"': "G3SG1",
        '"weapon_scar20_prefab"': "SCAR-20",
        '"weapon_ssg08_prefab"': "SSG 08",
        '"weapon_mag7_prefab"': "MAG-7",
        '"weapon_nova_prefab"': "Nova",
        '"weapon_sawedoff_prefab"': "Sawed-Off",
        '"weapon_xm1014_prefab"': "XM1014",
        '"weapon_m249_prefab"': "M249",
        '"weapon_negev_prefab"': "Negev",
        '"weapon_decoy_prefab"': "Diversion Device",
        '"weapon_diversion_prefab"': "Diversion Device",
        '"weapon_flashbang_prefab"': "High Explosive Grenade",
        '"weapon_hegrenade_prefab"': "High Explosive Grenade",
        '"weapon_frag_grenade_prefab"': "Frag Grenade",
        '"weapon_incgrenade_prefab"': "Incendiary Grenade",
        '"weapon_molotov_prefab"': "Smoke Grenade",
        '"weapon_firebomb_prefab"': "Smoke Grenade",
        '"weapon_smokegrenade_prefab"': "Smoke Grenade",
        '"weapon_tagrenade_prefab"': "Tactical Awareness Grenade",
        '"weapon_snowball_prefab"': "Snowball",
        '"weapon_m4a1_silencer_prefab"': "M4A1-S",
        '"weapon_usp_silencer_prefab"': "USP-S",
        '"weapon_revolver_prefab"': "R8 Revolver",
        '"weapon_taser_prefab"': "Zeus x27",
        '"weapon_zone_repulsor_prefab"': "Repulsor Device",
        '"weapon_shield_prefab"': "Riot Shield",
        '"weapon_breachcharge_prefab"': "Breach Charge",
        '"weapon_bumpmine_prefab"': "Medi-Shot",
        '"weapon_healthshot_prefab"': "Medi-Shot",
        '"weapon_fists_prefab"': "Bare Hands",
        '"weapon_tablet_prefab"': "Tablet",
    }

    for item in new_items.keys():
        if new_items[item][0] == 'Consumer':
            continue
        tmp = ''
        id = 0
        tag = 'PaintKit_' + re.search('(?<=\[).+(?=\])', item)[0] + '_Tag'
        floats = []
        for id2, line in enumerate(current_names[::-1]):
            if tag in line:
                line = line[:line.rfind('"')]
                tmp = line[line.rfind('"') + 1:]
                while True:
                    id2 -= 1
                    if len(floats) == 2:
                        break
                    if '"wear_remap_min"' in current_items[-1 - id2] or '"wear_remap_max"' in current_items[-1 - id2]:
                        fl = current_items[-1 - id2]
                        fl = fl[:fl.rfind('"')]
                        fl = fl[fl.rfind('"') + 1:]
                        floats.append(float(fl))
                break
        if not tmp:
            for i in current_items:
                if '"name"\t\t"' + re.search('(?<=\[).+(?=\])', item)[0] + '"' in i:
                    break
                id += 1
            while True:
                id += 1
                if id >= len(current_items) or (tmp != '' and len(floats) == 2):
                    floats.sort()
                    break
                if '"description_tag"' in current_items[id]:
                    tag = re.search('PaintKit.+(?=")', current_items[id])[0]
                    for line in current_names[::-1]:
                        if tag in line:
                            line = line[:line.rfind('"')]
                            tmp = line[line.rfind('"') + 1:]
                elif '"wear_remap_min"' in current_items[id] or '"wear_remap_max"' in current_items[id]:
                    fl = current_items[id]
                    fl = fl[:fl.rfind('"')]
                    fl = fl[fl.rfind('"') + 1:]
                    floats.append(float(fl))
        exteriors = []
        if floats[1] > 0.45:
            exteriors.append('Battle-Scarred')
        if floats[1] > 0.38 and floats[0] < 0.45:
            exteriors.append('Well-Worn')
        if floats[1] > 0.15 and floats[0] < 0.38:
            exteriors.append('Field-Tested')
        if floats[1] > 0.07 and floats[0] < 0.15:
            exteriors.append('Minimal Wear')
        if floats[0] < 0.07:
            exteriors.append('Factory New')
        weapon_string = '"' + item[item.find(']') + 1:-1] + '_prefab"'
        if weapon_string not in weapon_types.keys():
            continue
        weapon_type = weapon_types[weapon_string]
        tmp = weapon_type + ' | ' + tmp
        if new_items[item][1] not in parsed_names:
            parsed_names[new_items[item][1]] = [(tmp, new_items[item][0], exteriors)]
        elif (tmp, new_items[item][0]) not in parsed_names[new_items[item][1]]:
            parsed_names[new_items[item][1]].append((tmp, new_items[item][0], exteriors))

    if parsed_names:
        with open("new_weapons.html", "w", encoding='utf-8') as output:
            for collection in parsed_names.keys():
                output.write(f'<p style="font-size: 30px; text-decoration: none">{collection}</p>')
                for item in parsed_names[collection]:
                    output.write(f'<p style="font-size: 15px; text-decoration: none">{item[0]} ({item[1]})')
                    for exterior in item[2]:
                        output.write(f'....<a style="font-size: 20px; text-decoration: none" href="https://steamcommunity.com/market/listings/730/{item[0]} ({exterior})">{exterior}</a>')
                    output.write('</p>')

    return parsed_names
