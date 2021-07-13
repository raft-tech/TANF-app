import { createServer, Response } from 'miragejs'
import faker from 'faker'

export default function startMirage(
  { environment } = { environment: 'development' }
) {
  return createServer({
    environment,

    routes() {
      this.urlPrefix = 'http://localhost:8080/v1'

      this.post('/reports/', () => {
        return 'Success'
      })
      this.get('/login/oidc', () => {
        if (!window.localStorage.getItem('loggedIn')) {
          return Response(302, {
            location: 'http://localhost:3000/login/',
          })
        } else {
          return Response(401)
        }
      })
      this.get('/logout/', () => {
        if (window.localStorage.getItem('loggedIn')) {
          window.localstorage.setItem('loggedIn', false)
          return Response(302, {
            location: 'http://localhost:3000/logout/',
          })
        } else {
          return Response(401)
        }
      })
      this.get('/logout/oidc/', () => {
        return Response(302, {
          location: '/logout/',
        })
      })
      this.get('/auth_check/', () => {
        if (
          window.localStorage.getItem('loggedIn') ||
          process.env.REACT_APP_PA11Y_TEST
        ) {
          return {
            authenticated: true,
            user: {
              id: faker.datatype.uuid(),
              first_name: faker.name.firstName(),
              last_name: faker.name.lastName(),
              email: faker.internet.email(),
              stt: {
                id: 31,
                type: 'state',
                code: 'NJ',
                name: 'New Jersey',
              },
              roles: [],
            },
          }
        } else {
          return {
            authenticated: false,
          }
        }
      })
      this.patch('/users/set_profile', () => {
        return {}
      })
      this.get('/stts/alpha', () => [
        {
          id: 1,
          type: 'state',
          code: 'AL',
          name: 'Alabama',
        },
        {
          id: 2,
          type: 'state',
          code: 'AK',
          name: 'Alaska',
        },
        {
          id: 3,
          type: 'state',
          code: 'AZ',
          name: 'Arizona',
        },
        {
          id: 4,
          type: 'state',
          code: 'AR',
          name: 'Arkansas',
        },
        {
          id: 5,
          type: 'state',
          code: 'CA',
          name: 'California',
        },
        {
          id: 6,
          type: 'state',
          code: 'CO',
          name: 'Colorado',
        },
        {
          id: 7,
          type: 'state',
          code: 'CT',
          name: 'Connecticut',
        },
        {
          id: 8,
          type: 'state',
          code: 'DE',
          name: 'Delaware',
        },
        {
          id: 9,
          type: 'state',
          code: 'DC',
          name: 'District of Columbia',
        },
        {
          id: 10,
          type: 'state',
          code: 'FL',
          name: 'Florida',
        },
        {
          id: 11,
          type: 'state',
          code: 'GA',
          name: 'Georgia',
        },
        {
          id: 12,
          type: 'state',
          code: 'HI',
          name: 'Hawaii',
        },
        {
          id: 13,
          type: 'state',
          code: 'ID',
          name: 'Idaho',
        },
        {
          id: 14,
          type: 'state',
          code: 'IL',
          name: 'Illinois',
        },
        {
          id: 15,
          type: 'state',
          code: 'IN',
          name: 'Indiana',
        },
        {
          id: 16,
          type: 'state',
          code: 'IA',
          name: 'Iowa',
        },
        {
          id: 17,
          type: 'state',
          code: 'KS',
          name: 'Kansas',
        },
        {
          id: 18,
          type: 'state',
          code: 'KY',
          name: 'Kentucky',
        },
        {
          id: 19,
          type: 'state',
          code: 'LA',
          name: 'Louisiana',
        },
        {
          id: 20,
          type: 'state',
          code: 'ME',
          name: 'Maine',
        },
        {
          id: 21,
          type: 'state',
          code: 'MD',
          name: 'Maryland',
        },
        {
          id: 22,
          type: 'state',
          code: 'MA',
          name: 'Massachusetts',
        },
        {
          id: 23,
          type: 'state',
          code: 'MI',
          name: 'Michigan',
        },
        {
          id: 24,
          type: 'state',
          code: 'MN',
          name: 'Minnesota',
        },
        {
          id: 25,
          type: 'state',
          code: 'MS',
          name: 'Mississippi',
        },
        {
          id: 26,
          type: 'state',
          code: 'MO',
          name: 'Missouri',
        },
        {
          id: 27,
          type: 'state',
          code: 'MT',
          name: 'Montana',
        },
        {
          id: 28,
          type: 'state',
          code: 'NE',
          name: 'Nebraska',
        },
        {
          id: 29,
          type: 'state',
          code: 'NV',
          name: 'Nevada',
        },
        {
          id: 30,
          type: 'state',
          code: 'NH',
          name: 'New Hampshire',
        },
        {
          id: 31,
          type: 'state',
          code: 'NJ',
          name: 'New Jersey',
        },
        {
          id: 32,
          type: 'state',
          code: 'NM',
          name: 'New Mexico',
        },
        {
          id: 33,
          type: 'state',
          code: 'NY',
          name: 'New York',
        },
        {
          id: 34,
          type: 'state',
          code: 'NC',
          name: 'North Carolina',
        },
        {
          id: 35,
          type: 'state',
          code: 'ND',
          name: 'North Dakota',
        },
        {
          id: 36,
          type: 'state',
          code: 'OH',
          name: 'Ohio',
        },
        {
          id: 37,
          type: 'state',
          code: 'OK',
          name: 'Oklahoma',
        },
        {
          id: 38,
          type: 'state',
          code: 'OR',
          name: 'Oregon',
        },
        {
          id: 39,
          type: 'state',
          code: 'PA',
          name: 'Pennsylvania',
        },
        {
          id: 40,
          type: 'state',
          code: 'RI',
          name: 'Rhode Island',
        },
        {
          id: 41,
          type: 'state',
          code: 'SC',
          name: 'South Carolina',
        },
        {
          id: 42,
          type: 'state',
          code: 'SD',
          name: 'South Dakota',
        },
        {
          id: 43,
          type: 'state',
          code: 'TN',
          name: 'Tennessee',
        },
        {
          id: 44,
          type: 'state',
          code: 'TX',
          name: 'Texas',
        },
        {
          id: 45,
          type: 'state',
          code: 'UT',
          name: 'Utah',
        },
        {
          id: 46,
          type: 'state',
          code: 'VT',
          name: 'Vermont',
        },
        {
          id: 47,
          type: 'state',
          code: 'VA',
          name: 'Virginia',
        },
        {
          id: 48,
          type: 'state',
          code: 'WA',
          name: 'Washington',
        },
        {
          id: 49,
          type: 'state',
          code: 'WV',
          name: 'West Virginia',
        },
        {
          id: 50,
          type: 'state',
          code: 'WI',
          name: 'Wisconsin',
        },
        {
          id: 51,
          type: 'state',
          code: 'WY',
          name: 'Wyoming',
        },
        {
          id: 52,
          type: 'territory',
          code: 'AS',
          name: 'American Samoa',
        },
        {
          id: 53,
          type: 'territory',
          code: 'GU',
          name: 'Guam',
        },
        {
          id: 54,
          type: 'territory',
          code: 'MP',
          name: 'Northern Mariana Islands',
        },
        {
          id: 55,
          type: 'territory',
          code: 'PR',
          name: 'Puerto Rico',
        },
        {
          id: 56,
          type: 'territory',
          code: 'VI',
          name: 'Virgin Islands',
        },
        {
          id: 57,
          type: 'territory',
          code: 'US',
          name: 'Federal Government',
        },
        {
          id: 58,
          type: 'tribe',
          code: 'ME',
          name: 'Penobscot Nation',
        },
        {
          id: 59,
          type: 'tribe',
          code: 'NY',
          name: 'Seneca Nation of New York',
        },
        {
          id: 60,
          type: 'tribe',
          code: 'MS',
          name: 'Mississippi Band of Choctaw Indians',
        },
        {
          id: 61,
          type: 'tribe',
          code: 'NC',
          name: 'Eastern Band of Cherokee Indians',
        },
        {
          id: 62,
          type: 'tribe',
          code: 'MI',
          name: 'Sault Ste. Marie Tribe of Chippewa Indians',
        },
        {
          id: 63,
          type: 'tribe',
          code: 'MN',
          name: 'Leech Lake Band of Ojibwe',
        },
        {
          id: 64,
          type: 'tribe',
          code: 'MN',
          name: 'Mille Lacs Band of Ojibwe',
        },
        {
          id: 65,
          type: 'tribe',
          code: 'MN',
          name: 'Minnesota Chippewa Tribe',
        },
        {
          id: 66,
          type: 'tribe',
          code: 'MN',
          name: 'Red Lake Band of Chippewa Indians',
        },
        {
          id: 67,
          type: 'tribe',
          code: 'MN',
          name: 'White Earth Band of Chippewa Indians',
        },
        {
          id: 68,
          type: 'tribe',
          code: 'WI',
          name: 'Bad River Band of Lake Superior Tribe of Chippewa',
        },
        {
          id: 69,
          type: 'tribe',
          code: 'WI',
          name: 'Forest County Potawatomi Community',
        },
        {
          id: 70,
          type: 'tribe',
          code: 'WI',
          name: 'Ho-Chunk Nation',
        },
        {
          id: 71,
          type: 'tribe',
          code: 'WI',
          name: 'Lac Courte Oreilles Band of Lake Superior Ojibwe',
        },
        {
          id: 72,
          type: 'tribe',
          code: 'WI',
          name: 'Lac du Flambeau Band of Lake Superior Chippewa Indians',
        },
        {
          id: 73,
          type: 'tribe',
          code: 'WI',
          name: 'Menominee Indian Tribe',
        },
        {
          id: 74,
          type: 'tribe',
          code: 'WI',
          name: 'Oneida Tribe',
        },
        {
          id: 75,
          type: 'tribe',
          code: 'WI',
          name: 'Red Cliff Band of Lake Superior Chippewa Indians',
        },
        {
          id: 76,
          type: 'tribe',
          code: 'WI',
          name: 'Sokaogon Chippewa Community',
        },
        {
          id: 77,
          type: 'tribe',
          code: 'WI',
          name: 'Stockbridge-Munsee Community',
        },
        {
          id: 78,
          type: 'tribe',
          code: 'NM',
          name: 'Pueblo of Zuni',
        },
        {
          id: 79,
          type: 'tribe',
          code: 'NM',
          name: 'Mescalero Apache',
        },
        {
          id: 80,
          type: 'tribe',
          code: 'NM',
          name: 'Santo Domingo Tribe',
        },
        {
          id: 81,
          type: 'tribe',
          code: 'OK',
          name: 'Cheyenne and Arapaho Tribes of Oklahoma',
        },
        {
          id: 82,
          type: 'tribe',
          code: 'OK',
          name: 'Chickasaw Nation',
        },
        {
          id: 83,
          type: 'tribe',
          code: 'OK',
          name: 'Comanche Nation',
        },
        {
          id: 84,
          type: 'tribe',
          code: 'OK',
          name: 'Inter-Tribal Council, Inc.',
        },
        {
          id: 85,
          type: 'tribe',
          code: 'OK',
          name: 'Muscogee Creek Nation',
        },
        {
          id: 86,
          type: 'tribe',
          code: 'OK',
          name: 'Osage Nation of Oklahoma',
        },
        {
          id: 87,
          type: 'tribe',
          code: 'OK',
          name: 'Sac and Fox Nation',
        },
        {
          id: 88,
          type: 'tribe',
          code: 'KS',
          name: 'Kickapoo Tribe in Kansas',
        },
        {
          id: 89,
          type: 'tribe',
          code: 'KS',
          name: 'Prairie Band Potawatomi Nation',
        },
        {
          id: 90,
          type: 'tribe',
          code: 'NE',
          name: 'Omaha Tribe of Nebraska',
        },
        {
          id: 91,
          type: 'tribe',
          code: 'NE',
          name: 'Santee Sioux Nation',
        },
        {
          id: 92,
          type: 'tribe',
          code: 'NE',
          name: 'Winnebago Tribe',
        },
        {
          id: 93,
          type: 'tribe',
          code: 'MT',
          name: 'Assiniboine and Sioux Tribes of the Fort Peck Reservation',
        },
        {
          id: 94,
          type: 'tribe',
          code: 'MT',
          name: 'Blackfeet Tribe',
        },
        {
          id: 95,
          type: 'tribe',
          code: 'MT',
          name: "Chippewa-Cree Indians of the Rocky Boy's Reservation",
        },
        {
          id: 96,
          type: 'tribe',
          code: 'MT',
          name:
            'Confederated Salish & Kootenai Tribes of the Flathead Reservation',
        },
        {
          id: 97,
          type: 'tribe',
          code: 'MT',
          name: 'Fort Belknap Indian Community Council',
        },
        {
          id: 98,
          type: 'tribe',
          code: 'MT',
          name: 'Northern Cheyenne Tribe',
        },
        {
          id: 99,
          type: 'tribe',
          code: 'MT',
          name: 'Crow Tribe of Montana',
        },
        {
          id: 100,
          type: 'tribe',
          code: 'ND',
          name: 'Spirit Lake Sioux Tribe',
        },
        {
          id: 101,
          type: 'tribe',
          code: 'ND',
          name: 'Standing Rock Sioux Tribe',
        },
        {
          id: 102,
          type: 'tribe',
          code: 'ND',
          name: 'Three Affiliated Tribes',
        },
        {
          id: 103,
          type: 'tribe',
          code: 'ND',
          name: 'Turtle Mountain Band of Chippewa Indians',
        },
        {
          id: 104,
          type: 'tribe',
          code: 'SD',
          name: 'Cheyenne River Sioux Tribe',
        },
        {
          id: 105,
          type: 'tribe',
          code: 'SD',
          name: 'Lower Brule Sioux Tribe',
        },
        {
          id: 106,
          type: 'tribe',
          code: 'SD',
          name: 'Oglala Sioux Tribe',
        },
        {
          id: 107,
          type: 'tribe',
          code: 'SD',
          name: 'Rosebud Sioux Tribe',
        },
        {
          id: 108,
          type: 'tribe',
          code: 'SD',
          name: 'Sisseton - Wahpeton Oyate',
        },
        {
          id: 109,
          type: 'tribe',
          code: 'WY',
          name: 'Eastern Shoshone Tribe of the Wind River Reservation',
        },
        {
          id: 110,
          type: 'tribe',
          code: 'WY',
          name: 'Northern Arapaho Tribe of the Wind River Indian Reservation',
        },
        {
          id: 111,
          type: 'tribe',
          code: 'AZ',
          name: 'Cocopah Indian Tribe',
        },
        {
          id: 112,
          type: 'tribe',
          code: 'AZ',
          name: 'Gila River Indian Community',
        },
        {
          id: 113,
          type: 'tribe',
          code: 'AZ',
          name: 'Hopi Tribe',
        },
        {
          id: 114,
          type: 'tribe',
          code: 'AZ',
          name: 'Hualapai Indian Tribe',
        },
        {
          id: 115,
          type: 'tribe',
          code: 'AZ',
          name: 'Navajo Nation',
        },
        {
          id: 116,
          type: 'tribe',
          code: 'AZ',
          name: 'Pascua Yaqui',
        },
        {
          id: 117,
          type: 'tribe',
          code: 'AZ',
          name: 'Salt River - Pima Maricopa Indian Community',
        },
        {
          id: 118,
          type: 'tribe',
          code: 'AZ',
          name: 'San Carlos Apache Tribe',
        },
        {
          id: 119,
          type: 'tribe',
          code: 'AZ',
          name: "Tohono O'odham Nation",
        },
        {
          id: 120,
          type: 'tribe',
          code: 'AZ',
          name: 'White Mountain Apache Tribe',
        },
        {
          id: 121,
          type: 'tribe',
          code: 'CA',
          name: 'California Indian Manpower Consortium',
        },
        {
          id: 122,
          type: 'tribe',
          code: 'CA',
          name: 'Graton Rancheria',
        },
        {
          id: 123,
          type: 'tribe',
          code: 'CA',
          name: 'Hoopa Valley',
        },
        {
          id: 124,
          type: 'tribe',
          code: 'CA',
          name: 'Karuk Tribe',
        },
        {
          id: 125,
          type: 'tribe',
          code: 'CA',
          name: 'Morongo Band',
        },
        {
          id: 126,
          type: 'tribe',
          code: 'CA',
          name: 'North Fork Rancheria',
        },
        {
          id: 127,
          type: 'tribe',
          code: 'CA',
          name: 'Owens Valley Career Development Center',
        },
        {
          id: 128,
          type: 'tribe',
          code: 'CA',
          name: 'Pechanga',
        },
        {
          id: 129,
          type: 'tribe',
          code: 'CA',
          name: 'Robinson Rancheria/CTTP',
        },
        {
          id: 130,
          type: 'tribe',
          code: 'CA',
          name: 'Round Valley Indian Tribes',
        },
        {
          id: 131,
          type: 'tribe',
          code: 'CA',
          name: 'Scotts Valley',
        },
        {
          id: 132,
          type: 'tribe',
          code: 'CA',
          name:
            'Shingle Springs Band of Miwok Indians Shingle Springs Rancheria',
        },
        {
          id: 133,
          type: 'tribe',
          code: 'CA',
          name: 'Soboba Band of Luiseno Indians',
        },
        {
          id: 134,
          type: 'tribe',
          code: 'CA',
          name: "Southern California Tribal Chairmen's Association",
        },
        {
          id: 135,
          type: 'tribe',
          code: 'CA',
          name: 'Torres Martinez',
        },
        {
          id: 136,
          type: 'tribe',
          code: 'CA',
          name: 'Yurok Tribe',
        },
        {
          id: 137,
          type: 'tribe',
          code: 'CA',
          name: 'Tuolumne Band of Me-Wuk Indians',
        },
        {
          id: 138,
          type: 'tribe',
          code: 'NV',
          name: 'Shoshone- Paiute Tribes of the Duck Valley Reservation',
        },
        {
          id: 139,
          type: 'tribe',
          code: 'NV',
          name: 'Washoe Tribe',
        },
        {
          id: 140,
          type: 'tribe',
          code: 'AK',
          name: 'Aleutian/Pribilof Islands Association, Inc.',
        },
        {
          id: 141,
          type: 'tribe',
          code: 'AK',
          name: 'Association of Village Council Presidents',
        },
        {
          id: 142,
          type: 'tribe',
          code: 'AK',
          name: 'Bristol Bay Native Association',
        },
        {
          id: 143,
          type: 'tribe',
          code: 'AK',
          name: 'Central Council of the Tlingit and Haida Indian Tribes',
        },
        {
          id: 144,
          type: 'tribe',
          code: 'AK',
          name: 'Chugachmiut',
        },
        {
          id: 145,
          type: 'tribe',
          code: 'AK',
          name: 'Cook Inlet Tribal Council, Inc.',
        },
        {
          id: 146,
          type: 'tribe',
          code: 'AK',
          name: 'Kawerak, Inc.',
        },
        {
          id: 147,
          type: 'tribe',
          code: 'AK',
          name: 'Maniilaq Association',
        },
        {
          id: 148,
          type: 'tribe',
          code: 'AK',
          name: 'Metlakatla Indian Community',
        },
        {
          id: 149,
          type: 'tribe',
          code: 'AK',
          name: 'Tanana Chiefs Conference',
        },
        {
          id: 150,
          type: 'tribe',
          code: 'AK',
          name: 'Kodiak Area Native Assoc.',
        },
        {
          id: 151,
          type: 'tribe',
          code: 'ID',
          name: "Coeur d'Alene",
        },
        {
          id: 152,
          type: 'tribe',
          code: 'ID',
          name: 'Nez Perce',
        },
        {
          id: 153,
          type: 'tribe',
          code: 'ID',
          name: 'Shoshone - Bannock',
        },
        {
          id: 154,
          type: 'tribe',
          code: 'OR',
          name: 'Confederated Tribes of the Grand Ronde Community',
        },
        {
          id: 155,
          type: 'tribe',
          code: 'OR',
          name: 'Confederated Tribes of the Siletz Reservation',
        },
        {
          id: 156,
          type: 'tribe',
          code: 'OR',
          name: 'Klamath Tribes',
        },
        {
          id: 157,
          type: 'tribe',
          code: 'WA',
          name: 'Confederated Tribes and Bands of the Yakama Nation',
        },
        {
          id: 158,
          type: 'tribe',
          code: 'WA',
          name: 'Confederated Tribes of the Colville Reservation',
        },
        {
          id: 159,
          type: 'tribe',
          code: 'WA',
          name: 'Lower Elwha Tribe',
        },
        {
          id: 160,
          type: 'tribe',
          code: 'WA',
          name: 'Lummi Nation',
        },
        {
          id: 161,
          type: 'tribe',
          code: 'WA',
          name: 'Makah Indian Tribe',
        },
        {
          id: 162,
          type: 'tribe',
          code: 'WA',
          name: 'Nooksack Indian Tribe',
        },
        {
          id: 163,
          type: 'tribe',
          code: 'WA',
          name: "Port Gamble S'Klallam",
        },
        {
          id: 164,
          type: 'tribe',
          code: 'WA',
          name: 'Puyallup Tribe',
        },
        {
          id: 165,
          type: 'tribe',
          code: 'WA',
          name: 'Quileute Indian Tribe',
        },
        {
          id: 166,
          type: 'tribe',
          code: 'WA',
          name: 'Quinault Indian Nation',
        },
        {
          id: 167,
          type: 'tribe',
          code: 'WA',
          name: 'Sauk-Suiattle Indian Tribe',
        },
        {
          id: 168,
          type: 'tribe',
          code: 'WA',
          name: 'South Puget Inter-Tribal Planning Agency',
        },
        {
          id: 169,
          type: 'tribe',
          code: 'WA',
          name: 'Spokane',
        },
        {
          id: 170,
          type: 'tribe',
          code: 'WA',
          name: 'Stillaguamish Tribe',
        },
        {
          id: 171,
          type: 'tribe',
          code: 'WA',
          name: 'Swinomish Indian Tribal Community ',
        },
        {
          id: 172,
          type: 'tribe',
          code: 'WA',
          name: 'Tulalip Tribes',
        },
        {
          id: 173,
          type: 'tribe',
          code: 'WA',
          name: 'Upper Skagit Tribe',
        },
      ])
      this.get('/reports/', () => ({
        count: 2,
        next: null,
        previous: null,
        results: [
          {
            id: 1,
            original_filename: '2020.Q1.Active Case Data',
            slug: '2020.Q1.Active Case Data',
            extension: 'None',
            user: '0bc79b40-56b4-4a0e-9f3a-1894235c59a5',
            stt: 31,
            year: 2020,
            quarter: 'Q1',
            section: 'Active Case Data',
            created_at: '2021-07-07T16:41:15+0000',
          },
          {
            id: 2,
            original_filename: '2020.Q1.Active Case Data',
            slug: '2020.Q1.Active Case Data',
            extension: 'None',
            user: '0bc79b40-56b4-4a0e-9f3a-1894235c59a5',
            stt: 31,
            year: 2020,
            quarter: 'Q1',
            section: 'Active Case Data',
            created_at: '2021-07-07T16:41:36+0000',
          },
        ],
      }))

      // Allow unhandled requests to pass through
      this.passthrough(`${process.env.REACT_APP_BACKEND_URL}/**`)
      this.passthrough(`${process.env.REACT_APP_BACKEND_HOST}/**`)

      console.log('Done Building routes')
    },
  })
}
