# Title keywords vs what eBay UK buyers type

Source: eBay UK search-box suggestions (`autosug.ebaystatic.com`, site 3), which eBay ranks by how
often UK buyers search each phrase. Rebuild with `python3 research/keywords.py`.

Score: **3** = eBay suggests "X wall art / print / sign / poster" as soon as X is typed (strong);
**2** = suggested once the buyer adds wall/print/sign (real, narrower); **1** = searched, but not for
wall decor (e.g. 'sympathy' -> cards); **0** = nobody searches it.

## funny_sarcasm

| keyword | score | what buyers type |
|---|---|---|
| funny | 2 | funny wall art; funny signs / wall plaques; funny bathroom wall art |
| funny quote | 2 | funny quote prints; funny quote signs |
| funny sign | 2 | funny metal wall sign; funny toilet sign; no cold callers sign funny |
| rude | 2 | rude wall art; rude signs; rude sign |
| sarcastic | 1 | sarcastic mens t shirts; sarcastic t shirt; sarcastic funny t shirt womens |

## bathroom

| keyword | score | what buyers type |
|---|---|---|
| funny bathroom | 3 | funny bathroom wall art; funny bathroom pictures; funny bathroom signs |
| toilet rules | 3 | toilet rules sign |
| bathroom rules | 3 | bathroom rules sign |
| funny toilet | 3 | funny toilet sign; funny toilet pictures; funny toilet door signs |
| bathroom | 2 | bathroom wall art; bathroom prints; bathroom prints funny animal |
| toilet | 2 | toilet wall art; toilet wall pictures; toilet sign |

## hobbies

| keyword | score | what buyers type |
|---|---|---|
| funny | 2 | funny wall art; funny signs / wall plaques; funny bathroom wall art |
| fishing | 2 | fishing wall art; fishing sign; no fishing sign |
| golf | 2 | golf wall art; golf print; golf prints |
| knitting | 2 | cygnet pato baby prints dk knitting yarn; picture knitting patterns |
| gamer | 2 | gamer wall art |
| gaming | 2 | gaming wall art; gaming canvas wall art; gaming sign |
| craft room | 2 | craft room sign; craft room pictures |
| gardening | 1 | gardening gloves; gardening tool set; gardening tools |
| sewing room | 1 | sewing room clearout; sewing room furniture; craft room clearout sewing |

## heritage_dialect

| keyword | score | what buyers type |
|---|---|---|
| funny | 2 | funny wall art; funny signs / wall plaques; funny bathroom wall art |
| yorkshire | 2 | yorkshire print; david hockney yorkshire print; yorkshire sign |
| scottish | 2 | scottish wall art; scottish landscape art prints; scottish posters |
| northern | 2 | northern lights canvas wall art; northern soul wall art; northern soul prints |
| welsh | 2 | welsh wall plaque; welsh sign |
| irish | 2 | irish wall art; irish prints; irish sign |
| geordie | 1 | geordie vinyl; geordie greep; geordie cd |
| scouse | 1 | scouser fancy dress; scouse the mouse; scouse not english |
| cornish | 1 | cornish seaweed company; cornishware blue and white; cornish seaweed shampoo |

## man_cave

| keyword | score | what buyers type |
|---|---|---|
| man cave | 3 | man cave sign; man cave signs |
| funny man cave | 3 | funny man cave pub signs |
| garage | 2 | garage wall art; garage sign; garage signs metal |
| shed | 2 | shed signs personalised; shed signs; shed sign |

## laundry_utility

| keyword | score | what buyers type |
|---|---|---|
| laundry room | 3 | laundry room wall art; laundry room sign |
| utility room | 3 | utility room sign |
| funny laundry | 2 | funny laundry wall art; funny laundry prints |
| laundry | 2 | laundry room wall art; laundry prints; laundry sign |

## bar_pub

| keyword | score | what buyers type |
|---|---|---|
| pub | 3 | pub signs |
| home bar | 2 | home bar signs; bar signs for home bar; outside hanging pub sign for home bar |
| bar | 2 | bar wall art; bar signs for home bar; bar signs light up |
| beer | 2 | beer sign; beer signs metal; beer sign light |
| cocktail | 2 | cocktail sign; cocktail and dreams neon sign; cocktail bar sign |
| pub sign | 2 | vintage pub sign; original pub sign; antique pub sign |
| bar sign | 2 | neon bar sign; bar light sign led neon; personalised bar sign |
| gin | 2 | gin bar sign |

## coffee_cafe

| keyword | score | what buyers type |
|---|---|---|
| coffee bar | 3 | coffee bar sign |
| coffee station | 3 | coffee station sign |
| coffee | 2 | coffee wall art; but first coffee print; coffee sign |
| coffee quote | 2 | coffee quote prints; coffee quote signs |
| cafe | 2 | cafe wall art; cafe sign; cafe signs |
| tea | 2 | leopard print tea towels; tea sign; lyons tea enamel sign |

## kitchen

| keyword | score | what buyers type |
|---|---|---|
| funny kitchen | 3 | funny kitchen wall art; funny kitchen signs; funny kitchen wall art stickers quotes |
| kitchen rules | 3 | kitchen rules sign |
| kitchen | 2 | kitchen wall art; kitchen prints; kitchen prints a4 |
| kitchen quote | 2 | kitchen quote prints; kitchen quote signs |
| kitchen sign | 2 | kitchen wall sign; this kitchen is for dancing sign; kitchen rules sign |

## garden_outdoor

| keyword | score | what buyers type |
|---|---|---|
| garden | 2 | garden wall art; garden wall art metal; garden sign personalised |
| garden sign | 2 | personalised garden sign; welcome to my garden sign; robin garden sign |
| garden quote | 2 | garden quote prints; garden quote signs |
| outdoor | 2 | outdoor wall art; outdoor signs made to order; outdoor sign lights |

## faith_christian

| keyword | score | what buyers type |
|---|---|---|
| christian | 2 | christian wall art; christian cross wall hanging; christian canvas wall art |
| religious | 2 | religious wall plaque; religious wall hanging; wall plaque religious |
| jesus | 2 | jesus wall art; jesus canvas wall art; jesus christ wall art |
| faith | 2 | faith no more poster; george michael faith picture disc; faith no more picture disc |
| christian quote | 0 |  |

## scripture

| keyword | score | what buyers type |
|---|---|---|
| bible verse | 3 | bible verse wall art framed; bible verse wall art |
| scripture | 3 | scripture wall art |
| christian | 2 | christian wall art; christian cross wall hanging; christian canvas wall art |
| bible quote | 1 | bible quotes; bible quotes wall |
| psalm | 1 | psalm for the wild built; psalm 23; psalm 91 |

## faith_blessings

| keyword | score | what buyers type |
|---|---|---|
| religious | 2 | religious wall plaque; religious wall hanging; wall plaque religious |
| prayer | 2 | serenity prayer wall art; book of common prayer large print; madonna like a prayer poster |
| blessing | 1 | blessing of the oracle; blessing of the oracle foil; blessing clock |
| blessed | 1 | blessed rosary beads; blessed holy water; blessed virgin mary statue |
| house blessing | 0 |  |

## faith_islamic

| keyword | score | what buyers type |
|---|---|---|
| islamic | 3 | islamic wall art |
| arabic calligraphy | 3 | arabic calligraphy wall art |
| ayatul kursi | 3 | ayatul kursi wall art |
| muslim | 2 | muslim wall art |
| quran | 2 | quran wall art; large print quran |
| bismillah | 1 | bismillah wall sticker |

## faith_dharmic

| keyword | score | what buyers type |
|---|---|---|
| spiritual | 2 | spiritual wall art; spiritual wall hanging; spiritual pictures |
| buddha | 2 | buddha wall art; buddha wall plaque; buddha canvas wall art |
| hindu | 2 | hindu wall hanging; hindu wall art |
| zen | 2 | zen wall art; zen canvas wall art; zen stones wall art |
| om | 2 | om wall hanging |
| yoga | 1 | yoga mat; yoga blocks; yoga pants |

## memorial

| keyword | score | what buyers type |
|---|---|---|
| memorial | 3 | memorial plaque; memorial plaque for grave; memorial plaque for dogs |
| in loving memory | 3 | in loving memory plaque; in loving memory wedding sign |
| remembrance | 3 | remembrance plaque |
| sympathy | 1 | sympathy cards; sympathy cards thinking of you; sympathy card loss of mum |
| bereavement | 1 | bereavement gifts; bereavement cards; bereavement |
| grief | 1 | grief is the thing with feathers; grief works julia samuel; grief counseling and grief therapy |
| loss | 1 | loss of a dog; loss of a dog gift; lossga cabin bag |

## motivation

| keyword | score | what buyers type |
|---|---|---|
| motivational | 3 | motivational wall art; motivational gym posters; motivational poster |
| inspirational | 3 | inspirational quotes canvas wall art; inspirational quotes plaques; inspirational wall quote stickers |
| positive | 2 | positive wall art quotes |
| motivational quote | 1 | motivational quotes canvas wall art |
| positive quote | 1 | positive wall art quotes |
| affirmation | 1 | affirmation cards; affirmation cards for kids; positive affirmation cards |

## proverbs_classics

| keyword | score | what buyers type |
|---|---|---|
| inspirational | 3 | inspirational quotes canvas wall art; inspirational quotes plaques; inspirational wall quote stickers |
| inspirational quote | 2 | inspirational wall quote stickers; inspirational quote prints |
| quote | 2 | wall quote stickers; kitchen quote wall stickers; gym quote wall decals |
| life quote | 2 | life quote signs |
| wise quote | 0 |  |

## words_aesthetic

| keyword | score | what buyers type |
|---|---|---|
| minimalist | 3 | minimalist wall art |
| minimalist typography | 2 | minimalist typography wall art |
| typography | 2 | typography wall art |
| aesthetic | 2 | aesthetic posters |
| word art | 2 | word wall art; personalised word art print; word art poster print |
| quote | 2 | wall quote stickers; kitchen quote wall stickers; gym quote wall decals |

## office_work

| keyword | score | what buyers type |
|---|---|---|
| office | 2 | office wall art; office sign; office signs |
| office quote | 2 | office quote signs |
| work | 2 | workprint dvd; workprint; road work signs |
| home office | 2 | home office poster christmas |
| motivational office | 0 |  |

## fitness_selfcare

| keyword | score | what buyers type |
|---|---|---|
| motivational | 3 | motivational wall art; motivational gym posters; motivational poster |
| fitness | 2 | fitness poster |
| mental health | 2 | mental health posters |
| self care | 1 | self care journal; self care gift box; self care hamper |
| self love | 1 | self love; the self-love workbook for women |

## home_family

| keyword | score | what buyers type |
|---|---|---|
| family rules | 3 | family rules sign |
| house rules | 3 | house rules wall sign |
| family quote | 2 | family quote prints; family quote signs |
| family | 2 | family wall stickers quotes; family wall art; family wall sign |
| home quote | 2 | home quote prints; home quote signs |
| home | 2 | home wall art; home wall decor; home wall decorative art pictures frames |

## personalised_family

| keyword | score | what buyers type |
|---|---|---|
| personalised family | 3 | personalised family print; personalised family name plaque |
| personalised name | 3 | personalised name plaque |
| family name | 2 | family name signs; family name sign plaque; family name poster prints |
| personalised | 2 | personalised wall art; personalised wall plaque; personalised print |
| family tree | 2 | family tree picture frame |
| surname | 0 |  |

## wedding_love

| keyword | score | what buyers type |
|---|---|---|
| love quote | 3 | love quote prints |
| mr and mrs | 3 | mr and mrs sign |
| wedding love | 2 | wedding love sign letters |
| wedding | 2 | personalised wedding print; wedding sign stand; wedding signs |
| couple | 2 | couple wall art; couple prints |
| personalised wedding | 2 | personalised wedding print; personalised wedding welcome sign; personalised wedding picture frame |
| love | 2 | love wall art; love heart canvas wall art; live love laugh wall art |

## new_home

| keyword | score | what buyers type |
|---|---|---|
| new home | 2 | new home sign ornament; new home pictures |
| first home | 2 | first home pictures |
| housewarming | 1 | house warming gift; house warming gift for new home; house warming gifts new home |
| new home gift | 1 | new home gift; new home gifts ideas; new home gift personalised |

## milestones

| keyword | score | what buyers type |
|---|---|---|
| birthday | 2 | leopard print birthday decorations; leopard print birthday banner; birthday sign |
| anniversary | 2 | pokemon 30th anniversary poster collection; 30th anniversary poster collection; back to the future 40th anniversary poster |
| birthday gift | 1 | birthday gifts for her; birthday gifts for him; birthday gift bag |
| anniversary gift | 1 | anniversary gifts for her; anniversary gifts for him; anniversary gifts for couples |
| retirement gift | 1 | retirement gifts for women; retirement gifts for men; retirement gift bag |
| graduation gift | 1 | graduation gifts for her; graduation gifts for him; graduation gift bag |

## places_towns

| keyword | score | what buyers type |
|---|---|---|
| town | 2 | on town sign; town pictures |
| city | 2 | lego emerald city wall art; lego wicked emerald city wall art; pink city prints |
| hometown | 1 | jonas brothers greetings from your hometown; rohan hometown trousers; burton hometown hero |
| location | 1 | location boxer shorts; location tracker; location jacket |

## christmas_seasonal

| keyword | score | what buyers type |
|---|---|---|
| christmas | 2 | christmas wall hanging; christmas wall art; christmas sign |
| christmas quote | 2 | christmas quote prints; christmas quote signs |
| winter | 2 | winter wall art frame; winter scene art prints |
| festive | 1 | festive 67; festive lights; festive freeze topps 2026 |

## travel_coastal

| keyword | score | what buyers type |
|---|---|---|
| coastal | 3 | coastal wall art; coastal canvas wall art |
| seaside | 3 | seaside canvas wall art; seaside pictures |
| nautical | 3 | nautical wall art |
| beach | 2 | beach wall art; beach canvas wall art; sea beach canvas wall art |
| beach house | 2 | beach house pictures |

## nursery_kids

| keyword | score | what buyers type |
|---|---|---|
| nursery | 2 | nursery wall art; nursery wall hanging; baby nursery wall pictures |
| kids | 2 | kids on board car sign; personalised room signs kids; bedroom door name signs kids |
| kids room | 2 | kids room prints; kids room prints set; personalised room signs kids |
| baby | 2 | baby nursery wall pictures; cygnet pato baby prints dk knitting yarn; woolcraft baby print sparkle |
| childrens | 2 | childrens posters; childrens picture books bundle; childrens picture bible |
| nursery kids | 1 | nursery kids wallpaper |
| playroom | 1 | play room rug kids; playroom storage; playroom |

## classroom

| keyword | score | what buyers type |
|---|---|---|
| educational | 3 | educational posters |
| school | 2 | school sign; driving school roof sign; first day of school sign |
| classroom | 1 | classroom of the elite light novel; classroom of the elite; classroom chairs |
| teacher | 1 | teacher gifts; teacher planner; teacher stickers |
| classroom display | 1 | classroom display borders; classroom display |

## biz_education

| keyword | score | what buyers type |
|---|---|---|
| educational | 3 | educational posters |
| school | 2 | school sign; driving school roof sign; first day of school sign |
| classroom | 1 | classroom of the elite light novel; classroom of the elite; classroom chairs |
| teacher | 1 | teacher gifts; teacher planner; teacher stickers |
| classroom school | 0 |  |

## thank_you_jobs

| keyword | score | what buyers type |
|---|---|---|
| thank you | 2 | thank you picture frame |
| thank you gift | 1 | thank you gifts for women; thank you gift bags; thank you gifts |
| teacher gift | 1 | teacher gifts; teacher gifts end of year; teacher gift set |
| nurse gift | 1 | nurse gifts; nurse gift; student nurse gifts |
| leaving gift | 1 | leaving gifts for colleagues; leaving gifts for colleagues funny; leaving gifts for women |

## pets

| keyword | score | what buyers type |
|---|---|---|
| pet memorial | 3 | pet memorial plaque; pet memorial plaque for garden |
| dog | 2 | dog wall plaque; dog wall art; dog head wall plaque |
| cat | 2 | cat wall art; cat print; cat print scarf |
| dog quote | 2 | dog quote prints; dog quote signs |
| pet | 2 | pet dog memorial paw print; pet shop boys poster; pet shop boys obscure poster |
| dog lover | 1 | dog lover gifts; dog lover t shirt; gifts for dog lovers |
| cat lover | 1 | cat lovers gifts; cat lovers gifts for women; cat lovers birthday card |

## biz_automotive

| keyword | score | what buyers type |
|---|---|---|
| car showroom | 3 | car showroom posters; car showroom sign |
| car garage | 3 | car garage signs |
| garage | 2 | garage wall art; garage sign; garage signs metal |
| car | 2 | car wall art; car wall art metal; car prints |
| mechanic | 2 | mechanic posters |
| garage sign | 2 | garage wall sign; no parking in front of garage sign; vintage garage sign |

## biz_hair_beauty

| keyword | score | what buyers type |
|---|---|---|
| beauty room | 3 | beauty room sign |
| barber shop | 3 | barber shop sign; barber shop open sign |
| salon | 2 | hair salon wall art; salon posters |
| hair salon | 2 | hair salon wall art |
| beauty salon | 2 | beauty salon posters |
| barber | 2 | barber sign; barber shop sign; barber shop open sign |
| nail salon | 2 | nail salon wall art |

## biz_hospitality

| keyword | score | what buyers type |
|---|---|---|
| cafe | 2 | cafe wall art; cafe sign; cafe signs |
| restaurant | 2 | restaurant sign |
| cafe sign | 2 | vintage cafe sign; french cafe sign; hard rock cafe sign |
| cafe restaurant | 1 | cafe restaurant tables and chairs; restaurant cafe bar furniture |
| restaurant sign | 1 | restaurant sign |

## biz_fitness_venues

| keyword | score | what buyers type |
|---|---|---|
| gym motivational | 2 | motivational gym posters |
| gym | 2 | gym wall art; gym quote wall decals; gym sign |
| fitness | 2 | fitness poster |
| gym quote | 2 | gym quote signs |
| home gym | 2 | home gym sign; home gym pictures |

## biz_health

| keyword | score | what buyers type |
|---|---|---|
| medical | 2 | medical poster; vintage medical poster; antique medical poster |
| doctor | 2 | doctor who 3d print; doctor who print; 3d print doctor who |
| clinic | 1 | clinic clear body lotion; clinic clear; clinic plus shampoo |
| dental | 1 | dental cement; dental floss; dental tools |
| dentist | 1 | dentist tools; dentist plaque remover; dentist mirror |
| physio | 1 | physio resistance bands; physio tape; physio ball |
| therapy room | 0 |  |

## biz_office_pro

| keyword | score | what buyers type |
|---|---|---|
| office motivational | 2 | office motivational posters |
| office | 2 | office wall art; office sign; office signs |
| office quote | 2 | office quote signs |
| business | 2 | print business for sale; business signs; business signs made to order |
| entrepreneur | 1 | beyond entrepreneurship jim collins; the entrepreneurs marketing sales system |

## biz_retail_shop

| keyword | score | what buyers type |
|---|---|---|
| shop sign | 2 | antique shop sign; vintage shop sign; open sign for shop |
| shop | 2 | fantasy print shop; shop sign letters; shop sign |
| business | 2 | print business for sale; business signs; business signs made to order |
| shop decor | 2 | shop decor sign wooden; shop decor pictures |
| boutique | 1 | boutique teeth whitening gel; boutique teeth whitening gel 16; boutique hotel lego |

## biz_trades_pets

| keyword | score | what buyers type |
|---|---|---|
| workshop | 2 | workshop sign; workshop signs; personalised workshop sign |
| tattoo | 2 | tattoo wall art; tattoo print; tattoo print tights |
| barber | 2 | barber sign; barber shop sign; barber shop open sign |
| builder | 2 | bob the builder poster |
| dog grooming | 1 | dog grooming table; dog grooming bath; dog grooming clippers |
| electrician | 1 | electricians tools; electricians screwdriver set; electricians tool bag |

## img_animals

| keyword | score | what buyers type |
|---|---|---|
| highland cow | 3 | highland cow canvas |
| funny animal | 3 | funny animal canvas wall art |
| animal | 2 | animal wall art; animal wall art canvas print; animal print rug |
| animal bathroom | 2 | bathroom prints funny animal; animal bathroom pictures |
| dictionary | 2 | dictionary wall art; large print dictionary; large print scrabble dictionary |
| nursery animal | 2 | nursery animal signs; nursery animal posters; nursery animal pictures |
| woodland animal | 2 | woodland animal prints; woodland animal pictures |
| farm animal | 2 | farm animal prints; farm animal signs; vintage farm animal framed pictures |
| christmas animal | 2 | christmas animal signs; christmas animal posters; christmas animal pictures |
| royal animal | 2 | royal animal signs; royal animal posters; royal animal pictures |
| pet portrait | 2 | pet portrait wall art |
| animal in bath | 1 | animal in bathroom |
| dog in bath | 1 | dog in bathroom |
| flower crown | 1 | flower crown; flower crown headband; flower crown headband for wedding flower girl |
| black and white animal | 1 | black and white animal wallpaper; black white animal figurines |
| safari animal | 1 | safari animal cake toppers; safari animal toys; safari animals |
| animal flower crown | 0 |  |

## img_plants

| keyword | score | what buyers type |
|---|---|---|
| botanical | 3 | botanical prints framed; botanical prints; botanical prints vintage |
| flower | 2 | flower wall art; flower prints wall art; flower print |
| plant | 2 | wall hanging plant pots; set of 2 plant prints; plant pictures |
| wildflower | 2 | wildflower wall art; wild flower prints; wild flower sign |
| eucalyptus | 1 | eucalyptus oil; eucalyptus plant; eucalyptus tree |
| olive branch | 1 | olive branch; le creuset olive branch; artificial olive branches |

## charts

| keyword | score | what buyers type |
|---|---|---|
| educational | 3 | educational posters |
| periodic table | 3 | periodic table poster; periodic table with elements poster |
| solar system | 3 | solar system poster |
| times tables | 2 | times table poster |
| alphabet | 2 | alphabet wall hanging; alphabet poster |
| number | 2 | outdoor house wall number sign; wall number plaque; door number wall plaque |
| planets | 2 | battle of the planets poster |
| multiplication | 1 | multiplication table; multiplication pop it; multiplication |
| phonics | 1 | phonics flash cards; phonics reading books; phonics books |
| telling the time | 1 | telling the time clock; telling the time |
| roman numerals | 1 | roman numerals watch mens; roman numerals watch; roman numerals wall clock |
| feelings chart | 0 |  |

## maps

| keyword | score | what buyers type |
|---|---|---|
| world map | 3 | world map poster; world map canvas; world map wall art |
| uk map | 3 | uk map poster |
| map | 2 | world map wall art; world map canvas wall art; wooden world map wall art |
| england map | 2 | england map poster a1 |
| ireland map | 2 | ireland map picture framed |
| country map | 1 | london transport country bus map |
| home map | 1 | home map wallpaper; home map print fabric |
| map heart | 1 | map of the heart |
| scotland map | 1 | scotland map; road map of scotland; ordnance survey maps scotland |
| city map | 1 | gta vice city map; city of london map; vice city map |
| hometown map | 0 |  |

## pd_art

| keyword | score | what buyers type |
|---|---|---|
| botanical | 3 | botanical prints framed; botanical prints; botanical prints vintage |
| vintage map | 3 | vintage map framed |
| william morris | 3 | william morris prints |
| van gogh | 3 | van gogh prints |
| monet | 3 | monet canvas prints wall art |
| vintage poster | 3 | vintage poster framed |
| landscape | 3 | landscape canvas wall art; landscape oil painting framed; landscape paintings original art framed |
| seascape | 3 | seascape painting framed; seascape canvas wall art; seascape wall art |
| klimt | 3 | klimt print; klimt canvas; klimt framed |
| hokusai | 3 | hokusai print; hokusai woodblock print original; hokusai woodblock print |
| still life | 3 | still life painting framed; still life oil painting framed |
| old masters | 3 | old masters prints |
| abstract | 3 | abstract wall art; abstract painting on canvas; abstract canvas wall art |
| vintage botanical | 3 | vintage botanical prints; vintage botanical prints framed set; vintage botanical prints framed |
| vintage | 2 | vintage wall hanging; vintage wall art; vintage prints framed |
| japanese | 2 | japanese wall art; japanese wall hanging; japanese wall plaque |
| famous painting | 2 | famous painting wall art; famous painting prints |
| bird | 2 | bird wall plaque; bird wall hanging; bird wall art |
| horse | 2 | horse wall art stickers; horse wall plaque; horse wall art |
| museum | 2 | museum wall art; natural history museum print; museum poster |
| art nouveau | 2 | art nouveau wall plaque; art nouveau wall art; art nouveau wall hanging |
| vintage animal | 2 | animal print vintage african; vintage animal signs; vintage animal posters |
| fruit | 2 | fruit on canvas wall pictures; fruit print; blue print fruit machine |
| kitchen vintage | 2 | retro vintage metal tin kitchen signs; vintage kitchen signs; large vintage metal kitchen signs |

## product_nouns

| keyword | score | what buyers type |
|---|---|---|
| wall art | 3 | wall art canvas; wall art pictures living room framed large; wall art framed |
| art print | 3 | art print framed |
| wall decor | 3 | wall decor stickers self-adhesive wall art decals |
| framed wall art | 3 | framed wall art picture sets; framed wall art pictures flower canvas large; framed wall art picture new geometric horse |
| print | 2 | picasso print wall art canvas; large modern wall art canvas picture print; richard macneil canvas print wall art |
| prints | 2 | canvas prints wall art; wall art prints set of 3; monet canvas prints wall art |
| poster | 2 | poster wall art vintage food; poster prints wall art; wallace and gromit poster |
| picture | 2 | picture wall art; hard wall picture hooks; picture prints |
| framed print | 2 | pink peony wall art print silver framed; john lewis framed print; antique framed print |
| sign | 2 | walls ice cream sign; neon wall sign; outdoor house wall number sign |
| a4 print | 2 | large print word search books a4; a4 photo print; photo picture poster print art a0 a1 a2 a3 a4 |
| a3 print | 2 | photo picture poster print art a0 a1 a2 a3 a4; a3 photo print; a3 art print |
| a2 print | 2 | photo picture poster print art a0 a1 a2 a3 a4; a2 art print; painting print art poster a2 |
| unframed print | 1 | unframed prints; art prints unframed; wall art large picture prints unframed |

## used_in_titles

| keyword | score | what buyers type |
|---|---|---|
| barber shop | 3 | barber shop sign; barber shop open sign |
| bible verse | 3 | bible verse wall art framed; bible verse wall art |
| car showroom | 3 | car showroom posters; car showroom sign |
| coastal | 3 | coastal wall art; coastal canvas wall art |
| coffee bar | 3 | coffee bar sign |
| educational | 3 | educational posters |
| inspirational | 3 | inspirational quotes canvas wall art; inspirational quotes plaques; inspirational wall quote stickers |
| islamic | 3 | islamic wall art |
| laundry room | 3 | laundry room wall art; laundry room sign |
| love quote | 3 | love quote prints |
| man cave | 3 | man cave sign; man cave signs |
| memorial | 3 | memorial plaque; memorial plaque for grave; memorial plaque for dogs |
| minimalist | 3 | minimalist wall art |
| motivational | 3 | motivational wall art; motivational gym posters; motivational poster |
| mr and mrs | 3 | mr and mrs sign |
| pet memorial | 3 | pet memorial plaque; pet memorial plaque for garden |
| pub | 3 | pub signs |
| remembrance | 3 | remembrance plaque |
| scripture | 3 | scripture wall art |
| seaside | 3 | seaside canvas wall art; seaside pictures |
| anniversary | 2 | pokemon 30th anniversary poster collection; 30th anniversary poster collection; back to the future 40th anniversary poster |
| bathroom | 2 | bathroom wall art; bathroom prints; bathroom prints funny animal |
| beauty salon | 2 | beauty salon posters |
| birthday | 2 | leopard print birthday decorations; leopard print birthday banner; birthday sign |
| cafe | 2 | cafe wall art; cafe sign; cafe signs |
| christian | 2 | christian wall art; christian cross wall hanging; christian canvas wall art |
| christmas | 2 | christmas wall hanging; christmas wall art; christmas sign |
| couple | 2 | couple wall art; couple prints |
| family | 2 | family wall stickers quotes; family wall art; family wall sign |
| family name | 2 | family name signs; family name sign plaque; family name poster prints |
| funny | 2 | funny wall art; funny signs / wall plaques; funny bathroom wall art |
| garage | 2 | garage wall art; garage sign; garage signs metal |
| garden | 2 | garden wall art; garden wall art metal; garden sign personalised |
| graduation | 2 | kanye west graduation poster; graduation picture frames |
| gym | 2 | gym wall art; gym quote wall decals; gym sign |
| hair salon | 2 | hair salon wall art |
| home bar | 2 | home bar signs; bar signs for home bar; outside hanging pub sign for home bar |
| kids room | 2 | kids room prints; kids room prints set; personalised room signs kids |
| medical | 2 | medical poster; vintage medical poster; antique medical poster |
| muslim | 2 | muslim wall art |
| new home | 2 | new home sign ornament; new home pictures |
| nursery | 2 | nursery wall art; nursery wall hanging; baby nursery wall pictures |
| office | 2 | office wall art; office sign; office signs |
| positive | 2 | positive wall art quotes |
| religious | 2 | religious wall plaque; religious wall hanging; wall plaque religious |
| restaurant | 2 | restaurant sign |
| school | 2 | school sign; driving school roof sign; first day of school sign |
| shop | 2 | fantasy print shop; shop sign letters; shop sign |
| spiritual | 2 | spiritual wall art; spiritual wall hanging; spiritual pictures |
| thank you | 2 | thank you picture frame |
| toilet | 2 | toilet wall art; toilet wall pictures; toilet sign |
| town | 2 | on town sign; town pictures |
| typography | 2 | typography wall art |
| utility | 2 | utility room sign |
| wedding | 2 | personalised wedding print; wedding sign stand; wedding signs |
| workshop | 2 | workshop sign; workshop signs; personalised workshop sign |
| zen | 2 | zen wall art; zen canvas wall art; zen stones wall art |
| cat lover | 1 | cat lovers gifts; cat lovers gifts for women; cat lovers birthday card |
| classroom | 1 | classroom of the elite light novel; classroom of the elite; classroom chairs |
| clinic | 1 | clinic clear body lotion; clinic clear; clinic plus shampoo |
| dentist | 1 | dentist tools; dentist plaque remover; dentist mirror |
| dog lover | 1 | dog lover gifts; dog lover t shirt; gifts for dog lovers |
| housewarming | 1 | house warming gift; house warming gift for new home; house warming gifts new home |
| leaving gift | 1 | leaving gifts for colleagues; leaving gifts for colleagues funny; leaving gifts for women |
| nurse gift | 1 | nurse gifts; nurse gift; student nurse gifts |
| retirement | 1 | retirement gifts for women; retirement decorations; retirement gifts for men |
| teacher gift | 1 | teacher gifts; teacher gifts end of year; teacher gift set |
