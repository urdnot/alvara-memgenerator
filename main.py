import json

SETTINGS_JSON_PATH = 'settings.json'
MAX_OPTIONS_COUNT = 10
MAX_ATTR_COUNT = 7
OPTION_BITSIZE = 5


def _read_json(path):
    print("Read json file %s" % path)
    f = open(path, 'r')
    content = json.load(f)
    f.close()
    return content


def _add_name_to_register(mapping, united_str, name):
    if not name in mapping:
        name_shift = len(united_str)
        name_size = len(name)
        united_str += name
        mapping[name] = {'name_shift': name_shift, 'name_size': name_size}
    return united_str


def make_string_table(geometry):
    names = {}
    united_str = ""
    for cat in geometry['categories']:
        united_str = _add_name_to_register(names, united_str, cat['name'])
        for attr in cat['attributes']:
            united_str = _add_name_to_register(names, united_str, attr['name'])
    return united_str, names


def bin_rep(number, bit_size):
    bin_str = '{0:b}'.format(number)
    return bin_str.zfill(bit_size)


def make_attributes_table(geometry, names, register):
    #################################
    # Attr entry
    # --------------------------------
    # name_shift         2 * 8 bits
    # name_size          4 bits
    # place_multiplier   2 * 8 bits
    # --------------------------------
    register['ATTR_ENTRY_SIZE'] = 2 * 8 + 4 + 2 * 8
    register['ATTR_NAME_SHIFT_SHIFT'] = 0
    register['ATTR_NAME_SHIFT_SIZE'] = 2 * 8
    register['ATTR_NAME_SIZE_SHIFT'] = 2 * 8
    register['ATTR_NAME_SIZE_SIZE'] = 4
    register['PLACE_MULTIPLIER_SHIFT'] = 2 * 8 + 4
    register['PLACE_MULTIPLIER_SIZE'] = 2 * 8

    attrs = {}
    general = ""
    attr_count = 0
    cat_id = 0
    for cat in geometry['categories']:
        attrs[cat_id] = {
            'attr_start': attr_count,
            'attr_count': len(cat['attributes'])
        }
        multiplier = 1
        for attr in reversed(cat['attributes']):
            one = ""
            creds = names[attr['name']]
            one += bin_rep(creds['name_shift'], 2 * 8)
            one += bin_rep(creds['name_size'], 4)
            one += bin_rep(multiplier, 2 * 8)
            general = general + one
            multiplier *= len(attr['options'])
            attr_count += 1
        attrs[cat_id]['space_size'] = multiplier
        cat_id += 1
    return general, attrs


def make_ignored_table(geometry, register):
    ##################################
    # Ignore entry
    # ---------------------------------
    # ignore_mask       5 * 7 bits
    # place_mask        5 * 7 bits
    # ---------------------------------
    register['IGNORE_ENTRY_SIZE'] = 5 * 7 + 5 * 7
    register['IGNORE_MASK_SHIFT'] = 0
    register['IGNORE_MASK_SIZE'] = 5 * 7
    register['PLACE_MASK_SHIFT'] = 5 * 7
    register['PLACE_MASK_SIZE'] = 5 * 7

    ignores = {}
    general = ""
    ignores_count = 0
    cat_id = 0
    for cat in geometry['categories']:
        ignored_start = ignores_count
        for ignore in cat['ignored']:
            ignore_mask = ""
            place_mask = ""
            pos0 = ignore[0]
            op0 = ignore[1]
            pos1 = ignore[2]
            op1 = ignore[3]
            for i in range(0, MAX_ATTR_COUNT):
                if i == pos0:
                    ignore_mask += bin_rep(op0, 4)
                    place_mask += '11111'
                elif i == pos1:
                    ignore_mask += bin_rep(op1, 4)
                    place_mask += '11111'
                else:
                    ignore_mask += bin_rep(0, 4)
                    place_mask += '00000'
            general += ignore_mask + place_mask
            ignores_count += 1
        ignored_size = ignores_count - ignored_start
        ignores[cat_id] = {'ignored_start': ignored_start, 'ignored_size': ignored_size}
        cat_id += 1
    return general, ignores


def make_included_table(geometry, register):
    ##################################
    # Include entry
    # ---------------------------------
    # options_array     5 * 7 bits
    # ---------------------------------
    register['INCLUDE_ENTRY_SIZE'] = 5 * 7
    register['OPTIONS_ARRAY_SHIFT'] = 0
    register['OPTIONS_ARRAY_SIZE'] = 5 * 7

    includes = {}
    general = ""
    includes_count = 0
    cat_id = 0
    for cat in geometry['categories']:
        included_start = includes_count
        for include in cat['included']:
            one = ""
            for i in range(0, MAX_ATTR_COUNT):
                one += bin_rep(include[i], 5)
            general += one
            includes_count += 1
        included_size = includes_count - included_start
        includes[cat_id] = {'included_start': included_start, 'included_size': included_size}
        cat_id += 1
    return general, includes


def make_random_category_table(geometry, register):
    #################################
    # Random category entry
    # --------------------------------
    # range_size         13    bits
    # --------------------------------
    register['RCATEGORY_ENTRY_SIZE'] = 13
    register['RANGE_SIZE_SHIFT'] = 0
    register['RANGE_SIZE_SIZE'] = 13

    general = ""
    for cat in geometry['categories']:
        included_size = len(cat['included'])
        normal_size = cat['size'] - included_size
        general = bin_rep(normal_size, 13) + general
        general = bin_rep(included_size, 13) + general
    return general


def make_category_table(geometry, names, attrs, ignores, includes, register):
    #################################
    # Category entry
    # --------------------------------
    # name_shift         2 * 8 bits
    # name_size          4     bits
    # attr_start         8     bits
    # attr_count         3     bits
    # ignored_start      8     bits
    # ignored_size       4     bits
    # included_start     8     bits
    # included_size      4     bits
    # space_size         4 * 8 bits
    # --------------------------------
    register['CATEGORY_ENTRY_SIZE'] = 2 * 8 + 4 + 8 + 3 + 8 + 4 + 8 + 4 + 4 * 8
    register['CATEGORY_NAME_SHIFT_SHIFT'] = 0
    register['CATEGORY_NAME_SHIFT_SIZE'] = 2 * 8
    register['CATEGORY_NAME_SIZE_SHIFT'] = 2 * 8
    register['CATEGORY_NAME_SIZE_SIZE'] = 4
    register['ATTR_START_SHIFT'] = 2 * 8 + 4
    register['ATTR_START_SIZE'] = 8
    register['ATTR_COUNT_SHIFT'] = 2 * 8 + 4 + 8
    register['ATTR_COUNT_SIZE'] = 3
    register['IGNORED_START_SHIFT'] = 2 * 8 + 4 + 8 + 3
    register['IGNORED_START_SIZE'] = 8
    register['IGNORED_SIZE_SHIFT'] = 2 * 8 + 4 + 8 + 3 + 8
    register['IGNORED_SIZE_SIZE'] = 4
    register['INCLUDED_START_SHIFT'] = 2 * 8 + 4 + 8 + 3 + 8 + 4
    register['INCLUDED_START_SIZE'] = 8
    register['INCLUDED_SIZE_SHIFT'] = 2 * 8 + 4 + 8 + 3 + 8 + 4 + 8
    register['INCLUDED_SIZE_SIZE'] = 4
    register['SPACE_SIZE_SHIFT'] = 2 * 8 + 4 + 8 + 3 + 8 + 4 + 8 + 4
    register['SPACE_SIZE_SIZE'] = 4 * 8

    general = ""
    cat_id = 0
    for cat in geometry['categories']:
        one = ""
        creds = names[cat['name']]
        one += bin_rep(creds['name_shift'],                           2 * 8)
        one += bin_rep(creds['name_size'],                          4)
        one += bin_rep(attrs[cat_id]['attr_start'],             8)
        one += bin_rep(attrs[cat_id]['attr_count'],             3)
        one += bin_rep(ignores[cat_id]['ignored_start'],        8)
        one += bin_rep(ignores[cat_id]['ignored_size'],         4)
        one += bin_rep(includes[cat_id]['included_start'],      8)
        one += bin_rep(includes[cat_id]['included_size'],       4)
        one += bin_rep(attrs[cat_id]['space_size'],             4 * 8)
        general += one
        cat_id += 1
    return general


def bin2uint256hex(bin_str):
    result = []
    while len(bin_str) > 0:
        cur = bin_str[:256]
        bin_str = bin_str[256:]
        if len(cur) < 256:
            cur = cur + '0' * (256 - len(cur))
        result.append(int(cur, 2))
    return result


def main():
    register = {}
    register['OPTION_BITSIZE'] = OPTION_BITSIZE
    geometry = _read_json(SETTINGS_JSON_PATH)
    string_table, names = make_string_table(geometry)
    attr_table, attrs = make_attributes_table(geometry, names, register)
    ignored_table, ignores = make_ignored_table(geometry, register)
    included_table, includes = make_included_table(geometry, register)
    random_category_table = make_random_category_table(geometry, register)
    category_table = make_category_table(geometry, names, attrs, ignores, includes, register)

    general = category_table
    register['RANDOM_CATEGORY_TABLE_SHIFT'] = len(general)
    register['RANDOM_CATEGORY_TABLE_SIZE'] = len(random_category_table)
    general += random_category_table
    register['ATTR_TABLE_SHIFT'] = len(general)
    general += attr_table
    register['IGNORED_TABLE_SHIFT'] = len(general)
    general += ignored_table
    register['INCLUDED_TABLE_SHIFT'] = len(general)
    general += included_table

    uint256hex = bin2uint256hex(general)
    final = {
        'names': string_table,
        'hex': uint256hex,
        'register': register,
        'bin': general
    }
    final_str = json.dumps(final, indent=4)
    with open('memory.json', 'w') as out:
        out.write(final_str)


if __name__ == '__main__':
    main()


#################################
#  Const data
#--------------------------------
# Category entry 0
#--------------------------------
# name_shift         2 * 8 bits
# name_size          4     bits
# attr_start         8     bits
# attr_count         3     bits
# ignored_start      8     bits
# ignored_size       4     bits
# included_start     8     bits
# included_size      4     bits
# space_size         4 * 8 bits
#--------------------------------
# Category entry 1
# ...
#################################
# Random category entry 0
#--------------------------------
# range_size         13    bits
#--------------------------------
# Random category entry 1
# ...
#################################
# Attr entry 0
#--------------------------------
# name_shift         2 * 8 bits
# name_size          4 bits
# place_multiplier   2 * 8 bits
#---------------------------------
# Attr entry 1
# ...
##################################
# Ignore entry 0
#---------------------------------
# ignore_mask       5 * 7 bits
# place_mask        5 * 7 bits
#---------------------------------
# Ignore entry 1
# ...
##################################
# Include entry 0
#---------------------------------
# options_array     5 * 7 bits
#---------------------------------
# Include entry 1
# ...
