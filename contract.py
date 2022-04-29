import json

# function chooseRandomCategory() internal returns(uint8 rcid)
# {
# //  # --------------------------------
# //  # Random category entry
# //  # --------------------------------
# //  # rangeSize         13    bits
#
#     uint16 rnd = random(TOTAL_SUPPLY);
#     uint allRanges = load(435 / * RANDOM_CATEGORY_TABLE_SHIFT * /, 130 / * RANDOM_CATEGORY_TABLE_SIZE * /);
#     uint16 rangeEnd;
#     for (uint8 i = 0; i < 2 * CATEGORIES_COUNT; i++)
#     {
#         uint16 rangeSize = uint16(allRanges & 0x1fff);
#         rangeEnd += rangeSize;
#         allRanges >>= 13;
#
#         if (rnd < rangeEnd)
#         {
#             rcid = i;
#             while (curCategories[rcid] == rangeSize)
#             {
#                 rcid++;
#                 if (rcid >= CATEGORIES_COUNT)
#                 {
#                     rcid = 0;
#                 }
#             }
#             curCategories[rcid]++;
#             return rcid;
#         }
#     }
# }

TOTAL_SUPPLY = 10000
CATEGORY_COUNT = 5
curCategories = [0] * (2 * CATEGORY_COUNT)

def random(range):
    return 9800

def load(data, shift, bitSize):
    uint256mask = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
    end = shift + bitSize
    startId = shift >> 8
    finishId = end >> 8
    if startId == finishId:
        return ((data[startId] << (shift & 0xff)) & uint256mask) >> (256 - bitSize)
    else:
        sh1 = shift & 0xff
        sh2 = end & 0xff
        tmp1 = (((data[startId] << sh1) & uint256mask) >> (sh1 - sh2))
        tmp2 = data[finishId] >> (256 - sh2)
        return tmp1 + tmp2

def chooseRandomCategory(data):
    rnd = random(TOTAL_SUPPLY)
    allRanges = load(data, 435, 130)
    print(allRanges)
    rangeEnd = 0
    for i in range(0, 2 * CATEGORY_COUNT):
        rangeSize = allRanges & 0x1fff
        print(rangeSize)
        rangeEnd += rangeSize
        allRanges = allRanges >> 13

        if rnd < rangeEnd:
            rcid = i
            while curCategories[rcid] == rangeSize:
                rcid += 1
                if rcid >= 2 * CATEGORY_COUNT:
                    rcid = 0
            curCategories[rcid] += 1
            return rcid

def main():
    f = open('memory.json')
    mem = json.load(f)
    data = mem['hex']
    print(chooseRandomCategory(data))


if __name__ == '__main__':
    main()