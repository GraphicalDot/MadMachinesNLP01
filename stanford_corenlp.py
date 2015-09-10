#!/usr/bin/env python

import jsonrpclib




server = jsonrpclib.Server("http://localhost:3456")
result =  loads(server.parse("Bell, based in Los Angeles, it distributes electronic, computer and building products"))



for sent in tokenized_sentences:
        result = loads(server.parse(sent))
        sentences = result["sentences"]
        location = list()
        try:

                for __sent in sentences[0].get("words"):
                        if __sent[1].get("NamedEntityTag") == 'LOCATION':
                                location.append(__sent[0])
                if location:
                        print sent, "<------>", " ".join(location)
                        result.append([sent, " ".join(location)])
        except Exception as e:
                pass







["i've been wanting to go to this place since i first came to Gurgaon , 2 years ago .",
    "k ( 3 drinkers , 4 people in all ) which is what goes for 'slightly expensive ' in Gurgaon.",
    "easily the best cocktails in Delhi ncr .", 
    "now imagine an overcrowded place in gurgaon's summer where the ac isn't working.",
    "reminds you of London or New York bars ...",
    "we had really high expectations from this place due to their increasing popularity of cocktails in Gurgaon .",
    "this kind of outlets are there in Mumbai and Pune",
    "based on speakeasy concept during the prohibition era in America .",
    "the best craft cocktails i've had in Gurgaon .",
    "the service is not profit - maximization - focused , which is such a standout quality for a bar in Gurgaon .",
    "just reach out to Minakshi , the other owner .",
    "kinda reminds me of the pubs in Ireland specially around Belfast ..",
    "the name speakeasy was used to describe hidden bars in and around New York during the times when alcohol was prohibited .",
    "it was truly a pleasant experience to see that places like Speakeasy exist in India .",
    "after 2 hours of driving from Noida to Gurgaon , it was a disappointment not to get any parking space at Cyber Hub so we decided to visit this place since it has really good ratings on Zomato .",
    "the cocktails are innovative , tasty and unconventional and better than anything you'll get at any other bar in Gurgaon ."
    "the best cocktail bar in Delhi ncr .",
    "if you are in Gurgaon you definitely to need to give this place a go .",
    "it reminds me of The Prancing Pony in Bree from the movie lotr .",
    "you don't see such places in a huda market in Gurgaon .",
    "it is located in a residential shopping district as opposed to most cafes n pubs located in Gurgaon .",
    "perhaps this is one of the best places in India for cocktails as they are all so well mixed ."
    "was there on a Monday evening after the final weekend of great Diwali parties .",
    "another good place in Gurgaon to rejuvenate yourself with the choice of cocktails",
& nbsp ; It has been made in such a way to resemble the restaurants of the time 1920 - 1933 ( United States ) which used to sell alcohol illegally , as selling of alcohol was illegal in United States at that point of time  <------> United States United States
perhaps one of the best mixed drinks you can have in India . <------> India
this American style pub has a decent ambiance with a New York feel and the main seating in the basement . <------> New York
a lot of people recommended me this place and when i finally visited them on a saturday night , it was one of the worst experiences at a pub in Gurgaon . <------> Gurgaon
such establishments came into prominence in the United States during the Prohibition era ( 19201933 , longer in some states ) . <------> United States
during that time , the sale , manufacture , and transportation ( bootlegging ) of alcoholic beverages was illegal throughout the United States . <------> United States
easily the most charming bar in all of Delhi ncr for me . <------> Delhi
the first time i went there more than a year ago , and realised how the owners - Mr Yangdup ( a legend on the India map when it comes to cocktails ) and Minakshi who oversees the rest / resident quaffer - make it really special . <------> India
got that neighbourhood bar vibe , great music thrown in , the crowd has a great natural selection of 'chilled' people - very rare in Delhi and all those who go there know it . <------> Delhi
it is not one of the popular places of Gurgaon so if you land there by 7.30 pm , you will get great seating and happy hours till 8 pm . <------> Gurgaon
a breath of fresh air in gurgaon's pub clutter  <------> gurgaon
but they'll make you one if you ask ) and Manhattan ; a good thing is that they make these cocktails with bourbon ( Ok purists won't call jd / Jim Beam bourbons , <------> Manhattan
the only place that i've had comparable stuff in Delhi is pco , and that's much more expensive . <------> Delhi
it was really good and not same lame watered down crap that gets passed for cocktail around Delhi . <------> Delhi
3 ) The crowd that comes there isn't quite the best in Gurgaon by any means , and its relatively empty , which is a shame . <------> Gurgaon
gurgaon now has so many pubs , lounges , resto - bars ( call them what you will ) that it has arguably overtaken Bangalore as the pub capital of India . <------> Bangalore India
speakeasy is located in a sleepy - ish market in gurgaon's sector 15 and by the time we left around 11 pm the whole place was closed and dark , brilliantly reinforcing the feeling of actually having snuck a moonshine session in a back alley basement . <------> gurgaon
if you work in Gurgoan , there are two things you may or may not agree . <------> Gurgoan
:pcocktail and Dreams Speakeasy is strongly recommended because of the lovely drinks , decent food , awesome crowd , jazz nights , simple Ireland - ish interiors , sweet staff ( special mention of Meenakshi ) , reasonable prices , crazy memories , sweet celebrations and more . <------> Ireland
my favorite place in Gurgaon as of now . <------> Gurgaon
go there if you love cocktails , this is the best you can get in Delhi ncr , at the prices they charge . <------> Delhi
the place is in the Fab India market in sector 15 , is very little known and not crowded like some of the other popular joints in Gurgaon . <------> India Gurgaon
very cozy and different from all the usual pubs of Gurgaon ... <------> Gurgaon
a must go for anyone living / visiting Gurgaon  <------> Gurgaon
i've lived in States and Europe for quite a few number of years and have to say that this bar provides you with the comfort of the bar next door . <------> States Europe
i love experimenting with my cocktails and ever since i moved to India i had been craving to goto a bat that does bespoke cocktails . <------> India
:we stuck to the classics ( Mint julep and Negroni ) . <------> Negroni
just loved the apple cinnamon Mojita and Mint juleptheir cocktail workshop was a lot of fungiving 4 starts for all of the above <------> Mojita
the portion sizes are nothing like america ... <------> america
this cute little bar is one of the best cocktail bars that i have come across during my stay in Delhi . <------> Delhi
if u want awesome cocktails this is the best place in Gurgaon . <------> Gurgaon
the best drinks in Gurgaon and the food doesnt lag to far behind , infact the food is very good . <------> Gurgaon
being a regular visitor to Gurgaon , i decide to make the extra effort to hop across the highway to the dark side ( of Gurgaon ) and try the place . <------> Gurgaon Gurgaon
though in Delhi 500 for a cocktail is pretty standard , for a startup , most people might think its a bit on the expensive side . <------> Delhi
speakeasy has the formula down pat , and i think they should try and open shop somewhere a little more central and accessible , perhaps in Delhi , and are sure to do extremely well . <------> Delhi
keep it up , hope to see you in Delhi soon  <------> Delhi
i think this is the first of it's kind ( Speakeasy ) theme in Delhi . <------> Delhi
the place is located at a hush marketplace in Sec 15 , Gurgaon . <------> Gurgaon
i was served by ( arguably ) the best cocktail - connoisseur in India , Yangdup who made such great mixes that has made me a cocktail loyalist  <------> India
the ambiance has been thoughtfully done , true to the Speakeasy theme ( the american prohibition era concept ) . <------> american
) and the Manhattan and each of them were amazing . <------> Manhattan
this relatively new joint is the new kid on the block among the already enviable line up of places in Gurgaon compared to Delhi that have their own brewery or specialize in cocktails mixology . <------> Gurgaon Delhi
but on the other side of 15 sector market ( just behind Rasoi takeaway joint area ) . <------> Rasoi
most of the people who have grown up watching the American classics and the recent flick Great Gatsby would be familiar with the Speakeasy concept . <------> Great Gatsby
classics like the Bronx ( gin , orange juice ) , Foghorn ( gin n gingerale based ) , Mint julep , Old fashioned , Negroni , or make your own are very popular here . <------> Bronx Negroni
started off the evening with whatever you say cocktail which was okay kinds , my friends ordered Caprioska and some whiskey based cocktails which were quite nice . <------> Caprioska
after a long drive from South Delhi and some deliberations , we reached Speakeasy . <------> South Delhi
so happy to find a place that plays good Jazz in Gurgaon . <------> Gurgaon
so much so , i have never got a chance to repeat my drinks - - Gin and passion fruit based small drink - Gin and thyme based small drink - Tequila and watermelon based tall drink - White rum , blueberry marmalade and black grapes based tall drink - Peach and apricot flavored Margarita frozen - White rum , orange and caramel based tall drink - Red wine , orange , egg white based drink - Baileys flaming shots - Gin , orange and strawberry based small drinkmy friends have had - Baileys , kahlua mixed mid size drink - From the signature cocktails  <------> Tequila
old fashioned , Manhattan etc . <------> Manhattan
if you are cocktail lover than this the place in whole of Delhi . <------> Delhi
when you will be served from one of the best in beverage industry like Shariq Khan & amp ; Lamha . <------> Lamha
tucked away in the quieter corner of Gurgaon seems like the place was handpicked to give you a glimpse into the old prohibition era " no bling " policy . <------> Gurgaon
it came highly recommended so me and my friend made a trip from Delhi last friday . <------> Delhi
:chicken wings were the best ive had in india and the pigs in a blanket ( bacon wrapped around pork sausages ) were great too . <------> india
personally i liked the interior - it is more of a american sneak out kinda place . <------> american
now this is just the place we wanted in Gurgaon ... <------> Gurgaon
so glad i live in Gurgaon now and Gurgaon has this gem . <------> Gurgaon Gurgaon
well this place could be described as exactly what we needed close to home in Gurgaon . <------> Gurgaon
this is a great place tucked away in the most quietest of markets of Gurgaon . <------> Gurgaon
we went with Blueberry Bamble ( Vodka based ) , The Monkey Gland ( Absinthe based ) and Cocktail Special ( whiskey based ) along with Pig in a Blanker and Crispy Calamari for eating . <------> Bamble
blueberry Bamble mostly tasted of , well , Blueberry , and it was just like a regular cocktail . <------> Bamble
amazing surprise , that too in Gurgaon  <------> Gurgaon
such establishments came into prominence in the United States during the period known as Prohibition ( 1920 - 1933 , longer in some states ) . <------> United States
during this time , the sale , manufacture , and transportation ( bootlegging ) of alcoholic beverages was illegal throughout the United States . <------> United States
cocktails & amp ; dreams speakeasy is also made in a somewhat similar way - dark , occasional bulbs , waiters & amp ; bar - guys dressed up in Old American way . <------> Old American
not too many in Delhi make good Whiskey based - so let's try that' . <------> Delhi
his brother , an avid trekker , has worked in India & amp ; abroad in Restaurants & amp ; is quite a genius in coming up with simple lovable food . <------> India
there is no seafood in the menu as the Chef thinks 'Quality of seafood / fish is so bad here in Delhi - it will never match up to expectations of Globe - trotting customers . <------> Delhi
for pics of food at this place & amp ; also for reviews of other eateries in Gurgaon & amp ; Delhi including streetfood , pls visit my blog <------> Gurgaon Delhi
though i live in Delhi , i'll definitely be going back to Cocktails & amp ; Dreams - It was love at first sip  <------> Delhi
live in Gurgaon / South Delhi ? <------> Gurgaon South Delhi
welcome to Speakeasy - Cocktails and Dreams , Sector 15 , Gurgaon . <------> Gurgaon
coming from Delhi , you take a u - Turn from under the flyover on 8 <------> Delhi
it was a Monday evening when we visited ; also , the luck of Navratri going on ; ) was on our side . <------> Navratri
a place like this in Gurgaon , that too in sector 15  <------> Gurgaon
i have been living in the Delhi area for the last three years since my arrival from the States . <------> Delhi
i've wandered in town ( Delhi ) and around . <------> Delhi
mother Mary your mercy and thank your goodness for allowing me to stumble upon Cocktails and Dreams , Speakeasy in Gurgaon . <------> Gurgaon
cocktails & amp ; Dreams , Two perfect words for the heading of Speak Easy Bar in Sector 15 , Gurgaon . <------> Gurgaon
being in the beverage industry and for most the Cocktail industry , this is the best bar in Delhi / ncr for cocktails of this style . <------> Delhi
i liked taste of all items what we ordered except pad Thai noodles and Singapore lamb . <------> Singapore
people say that the outlet at Bani Square is amazing .... <------> Bani Square
a poorer younger cousin of berco's in India . <------> India
amazing Chinese in Gurgaon  <------> Gurgaon
the Hong Kong style chicken had way too many nuts for me - cashew and peanuts . <------> Hong Kong
chicken Hong Kong style and fried rice ... <------> Hong Kong
the most tasty food you can ever get in India with pure flavors of Thai / Chinese so try big Wong & nbsp ; you will love it in one words its osmmmmmmmmmm ........... <------> India
one of the few places to serve pan asian cuisine in Galleria , Big Wong is a cosy place located on the first floor . <------> Big Wong
however , for me as a Thai person from Bangkok , i start to like Indian style Thai foods . <------> Bangkok
hard to find in Galaria market . <------> Galaria
one of the best Thai joints in india . <------> india
i'm a great fan of Tom Yum and the soup here is the best i have had in india . <------> india
in fact have to say best Hakka noodles i have had in Gurgaon  <------> Gurgaon
they serve good quality food with fresh ingredients at cheap prices ( compared to others like Dine - sty or Mainland China ) . <------> China
but it's a tiny place that serves great Calcutta - style Chinese food  <------> Calcutta
& nbsp ; Competitiveness for chinese food is immense in Gurgaon and lacklustre preparations can put quite a dent on their reputation . <------> Gurgaon
main course was their house special chicken pan fried noodles and the Hong Kong style chicken which was pretty decent quantity wise and quite unusually delicious . <------> Hong Kong
the best Chinese food i have had in Gurgaon . <------> Gurgaon
no doubt the mother restaurant at Baani is my fav <------> Baani
we ordered Hong Kong style chicken which was good , classic garlic hot which was okayish , chicken pan fried noodles & nbsp ; and mixed fried noodles which were tasty. <------> Hong Kong
@better chinese is available in Gurgaon for same price and same vicinity ... <------> Gurgaon
they are different than the regular ones that we get at every corner in Delhi . <------> Delhi
it's my favorite in Gurgaon  <------> Gurgaon
luckily we got a seat in Big Wong . <------> Big Wong
glad it has opened a unit in Galaria ...... <------> Galaria
being a Malaysian Chinese working for a Fortune 500 Mainland Chinese company staying here in Gurgaon for business reasons , i must say that Big Wong really has given my taste - buds and tummy the antidote on cravings for decent Chinese food . <------> Gurgaon
i have tasted some of the chinese food establishments around Gurgaon area circa June '14 - July'14 and almost all of them tried to localize their dishes to the extend where the Chinese dishes had overbearing Indian - infused tinge to it . <------> Gurgaon
meanwhile Big Wong has managed to keep such preparations similar to what we Malaysian / Singaporeans have at home . <------> Malaysian
and should you decide to expand down south into South East Asian countries , i will be definitely the very first few to stand in line and welcome your arrival  <------> South East Asian
) , Hakka noodles and Chicken Hong Kong gravy . <------> Chicken Hong Kong
there was a tangy taste and coupled together with the absolutely awesome Hong Kong curry , let me say that our day ended in bliss  <------> Hong Kong
i was never really fond of chinese food until & nbsp ; i was introduced to the food of Big Wong by my friend who hadordered in from their outlet in Galeria . <------> Galeria
the poor momo , on the other hand , is native to Tibet , it is thick - skinned and has basic fillings such as ground meat . <------> Tibet
it is truly my favourite Chinese restaurant in Gurgaon . <------> Gurgaon
hope you guys keep rocking Gurgaon and go pan - India soon . <------> Gurgaon India
my wishes to the entire Big Wong team for many more outlets , not just in Gurgaon <------> Gurgaon
best chinese food i've had in India  <------> India
located at sec 29 , the gastronomic hub og Gurgaon , the place has lot to offer . <------> Gurgaon
recently i visited and tried there Matka Kulfi , Flavoured Milk or pista milk badam and yes the special real mango kulfi . <------> Matka Kulfi
:averageif you can handle the rudeness of ordering counter staff , you can go and enjoy the food at Bikanerwala . <------> Bikanerwala
coming to food , i had ordered noodles with Manchurian , north India thali , chaach and rasogulla . <------> India
then lots of Water in Handwash . <------> Handwash
& nbsp ; The chaat is nice , the Gajar ka Halwa awesome , the sweets are generally good to excellent . <------> Halwa
and if you happen to choose the dishes from both ground floor ( chat and fast food items ) and first floor ( North and South Indian main course ) then you will have to literally work to 'earn your bread'  <------> North
the First time i went to Delhi was on a Business trip last week . <------> Delhi
my office colleagues suggested to try this place and being from mumbai i thought this would be a small store with sevs and snacks <------> mumbai
the trip wasnt as boring as i expected thanks to Bikanerwala  <------> Bikanerwala
if you are a sweet - a - holic and looking for the sweets in Gurgaon , mark my words ; this is the best place you will ever find . <------> Gurgaon
the best part is that you can have everything which you love starting from snacks , sweets and street food anytime in Bikanervala . <------> Bikanervala
bikanervala is is one of the beat sweets shop chain in Delhi . <------> Delhi
i really loved the Rabri Falooda and Dahi Kachori . <------> Rabri Falooda
i loved the Choco nut sunday and the fruit sunday was awesome .. <------> Choco
it is undoubtedly one of the most trusted and renowned fast food brand in india . <------> india
there is Lassi ( Mango / Kesaria ) , Khus Sherbat , kanji et all to accompany and other chats and south indian stuff if you like ... <------> Kesaria
the garam garam Jalebi , Badam milk and fresh ras malai are the exit items for us to close a heavy breakfast ... <------> Badam
i like chole bhature , pav bhaji , baked biscuits and some of the sweets from Bikanervala . <------> Bikanervala
the place is just like all other Bikanervala and has a self service <------> Bikanervala
for those who havnt tried bikanerwaladahi Wadas and chole bature are awesomelaasi is a super hit to beat the summer heatrest all the sweets are amongst the best especially Gulab jamun and malpuas are awesome . <------> Wadas
the taste was very different from the similar items that we get at Mumbai . <------> Mumbai
i learned to love them from the market at Taj Palace in Bellevue , Washington , <------> Bellevue Washington
but the variety of different burfi at Bikanervala is many times bigger  <------> Bikanervala
i have tried their Masala Fish Curry , Eat - with - your - hands Kerala Grilled Chicken , Mustard tossed home fries , Malabari Kokum Mixed Veg Curry , Malabar Paratha , Appam , Hot Chocolate , Watermelon coolermasala Fish Curry - The gravy was thick and full of flavour from the masalas . <------> Kerala
eat - with - your - hands Kerala Grilled Chicken - The chicken was cooked to perfection and well seasoned . <------> Kerala
& nbsp ; Hot Chocolate - This has to be the thickest and the richest hot chocolate i have had in Delhi . <------> Delhi
bikanervala is quite a popular food joint in Gurgaon , specially for vegetarians . <------> Gurgaon
almost reaching the standards of Mumbai ... <------> Mumbai
one of the best self service / quick service restaurants in Gurgaon . <------> Gurgaon
the place can get crowded on special occasions ( Diwali , Holi , Etc. ) <------> Diwali Etc.
& nbsp ; They have good hygiene & amp ; food quality is top notch , whenever i feel like having the street foods of saddi Dilli in Gurgaon this is the place i head to . <------> Gurgaon
probably the best place for coastal food in Delhi .. <------> Delhi
i happened to chance upon this amazing restaurant while mindlessly walking through Haus Khas Village trying to identify a new outlet that i had not tried earlier and to be very honest i have been craving for some good homely South Indian curries having lived in Chennai & amp ; Hyderabad for over 5 years . <------> Haus Khas Village Chennai Hyderabad
i ordered a Chowpatti drink ( Aampanna & amp ; Tequila ) suggested by the staff since it complements the food very well . <------> Chowpatti
coming from Bangalore you're pretty aware of South Indian cuisine , so we stuck to the Kerala menu . <------> Bangalore Kerala
you certainly dont get to eat such brilliant south Indian coastal cuisine anywhere in Delhi which is not the typical Sarvana Bhavan - ish south Indian <------> Sarvana Bhavan
recently went to this undiscovered hidden restaurant which is located on the floor above Ogaan at the Hauz khas village . <------> Ogaan
the fragrances and ambience at this cafe in hauz khas village made me reminiscent my favorite holiday destination in the country - Goa ( All those who know the city of sin and pleasure understand when i say this - Goa is a hub for culinary fusions and discoveries ) . <------> Goa Goa
i have had their Goan prawn curry served with tangy chutneys , malabari paranthas and Kerala Fried Chicken as my staple dishes every time i visit the place . <------> Kerala
cafe's Malabar parotha is the best in Delhi ncr region . <------> Delhi
& nbsp ; On a good weather day , almost feels like one is in Goa . <------> Goa
finding a quiet place to have your meal in Hauz Khas over the weekend , can be quite a task . <------> Hauz Khas
we decided on the Chilli Olive Oil Tossed Prawns and the Original Baja California Fish Tacos to start our meal . <------> Baja California
along with our starters , we opted for a glass of Moscow Mule and two Kaffir Lime Tonics . <------> Moscow
i love Badam milk which they serve during the winters . <------> Badam
while my personal favourite remains Chola Batura , i've tried a lot of their stuff - thalis , dosas ( i like Rawa more ) , Idli , Sandwiches , Burgers , Pizza , Chinese ( The Platter is probably what you want to go for ) , Salad , Gol Gappas , Tikki etc . <------> Rawa Idli
as good as you can get down here in Delhi , alongside Zambar , Mandaa and Swagath ( earstwhile .. <------> Delhi Zambar Mandaa
we had Kerala Grilled Chicken for starters and it was literally amazing . <------> Kerala
:) The drinks - we had a moscow mule ( vodka , ginger ale and ginger ) , chowpatty ( aampanna and tequila martini ) , ipanema ( passion fruit based martini ) and a orange and basil margarita . <------> moscow ipanema
the cocktail moscow mule lacked the ginger punch that it promises . <------> moscow
absolutely best casual restaurant in Delhi  <------> Delhi
almost felt like i was dining somewhere in Thekkady  <------> Thekkady
kerala galore <------> kerala
they say , the 'Coast Cafe ' is the closest you can get to a coast in Delhi . <------> Delhi
the meat was so soft , the curry lush so much so it reminded me of the days i used to study in Bangalore . <------> Bangalore
their sweets are also much better than some of the other outlets in Gurgaon , especially their Mathura peda ( fresh out of the kitchen it just melts in your mouth and full of ghee ) . <------> Gurgaon Mathura
i liked Chole bhature , matara kulcha , kachoris , dhokla , raj kachori and the list is long . <------> matara
seriously avoid during Diwali time <------> Diwali
bikanerwala at sector 29 Gurgaon covers a big space . <------> Gurgaon
from Mumbai street food to Punjabi to Chinese .. <------> Mumbai
my favourites are the Chole Bhature and the Sweet Lassi which has been the best i have had in Delhi . <------> Delhi
a very overrated place in North Delhi with extremely poor service . <------> North Delhi
:dwe ordered chilli paneer , assorted veg platter , truffle shake , miami cooler and Berry blast . <------> miami
the tacos were certainly the best you get in Delhi on both occasions of my visit . <------> Delhi
this place happens to be first of the select few places that places that i have visited in Hauz Khas and one of the simplest in Delhi . <------> Delhi
a gorgeous place on the floor above Ogaan , this place has beautiful trellised windows with climbing vines , candlelit tables and a spacious top - floor seating area . <------> Ogaan
( plus it's easy to find , which is always a plus in Hauz Khas village ) . <------> Hauz Khas
:we had the chicken satay ( with an excellent peanut sauce ) , and the Kerala Grilled Chicken ( <------> Kerala
lovely decor , nice Kerala food , yummie cocktails . <------> Kerala
one of the best ambience in hkv , really good service and extremely decent Kerala food  <------> Kerala
india is a vast country which has different cultures that offers variety of cuisines to choose from . <------> india
today i explored one of the rich and distinct south Indian food - Kerala food , which stands out for the use of its spices . <------> Kerala
the cafe is divided into two floors above Ogaan which is a quite famous store . <------> Ogaan
stands out in the cacophony of Hauz Khas Village . <------> Hauz Khas Village
mutton sukka - nothing close to what you get in Kerala .. <------> Kerala
i have definitely had better coastal / Kerala food . <------> Kerala
:) so unlike a lot of restaurants in Hauz Khas Village , there is no need to climb narrow stairways . <------> Hauz Khas Village
the best part is its location , its right above the Ogaan showroom and the first restaurant you cross when entering this Urban Village . <------> Ogaan
but the appam's served here rate amongst the best served in Delhi ( and yes i have been to Dakshin ) . <------> Delhi
:coastal as the name suggests which translates to select cuisine from western coast of India . <------> India
but would only visit for the fine taste they offeri being from Hyderabad tried the chat here in Bikanervala for the first time . <------> Hyderabad Bikanervala
( i have never visited their branch in Hyderabad so can't really compare in terms of taste ) <------> Hyderabad
located in the middle of the ever so crowded Sector 29 in Gurgaon , Bikanervala offers an array of delicious desi food at very affordable rates . <------> Gurgaon
get much much better stuff in Jaipur at Kanjis and Rawats . <------> Jaipur Kanjis
the Bikaneri Boondi is very strange tasting and certainly not from Bikaner  <------> Bikaner
matar Kulcha , Rabri + Malpua , Idli + wada , rajkachori , chat platter , bhakarwadi , jalebi and jaggery rasgulla . <------> jaggery
there are so many varieties of food at Bikarnerwala , i wonder if anybody has tasted all of them . <------> Bikarnerwala
i have a sweet tooth and since Bikarnerwala had some special Winter desserts i was not able to resist myself in trying the Pineapple halwa and Gajar Halwa which were just yummmm .. <------> Gajar Halwa
-this Bikanerwala is also know as the Big Bikanerwala and located in the food circle of sector 29 . <------> Big Bikanerwala
sweets ( 5 / 5 ) - i personally don't think that there is any place in Gurgaon which serves better sweets than this Bikanerwala . <------> Gurgaon
but all the outlets of Bikanerwala . <------> Bikanerwala
i don't understand why the management at Bikanerwala do not understand that If a group / family comes together then they should be served food at the same time . <------> Bikanerwala
( which is higher then even no. 1 bakery of Gurgaon ) i am going to rate it 1.5 . <------> Gurgaon
if you living in Gurgaon and have a sweet tooth than you might have already visited this place . <------> Gurgaon
the place brings alive a refreshing college atmosphere with the cafe filled with students from North Campus , looking to chill out , enjoy some edm over hookah and drinks . <------> North Campus
at last we ordered some mocktails like cool miami and berry blast which were refreshing and amazed us . <------> miami
was in North Delhi with a group of friends and in urgent need of a place to just sit and chill . <------> North Delhi
:coastal as the name suggests which translates to select cuisine from western coast of India . <------> India
a dish from Goa , a dish or more from Coastal Karnataka , something from Kerala is what they have on offer and they have cracked most of it when it comes to authentic taste . <------> Goa Karnataka Kerala
it overlooks the outside of Hauzkhas village <------> Hauzkhas
the Avial was perfect - exactly what you would get in Cochin . <------> Cochin
although i can't vouch for authenticity given that i haven't had the real deal in Kerala . <------> Kerala
mutton Chukka  <------> Chukka
the total costs for 10 items minus the sweets was 500 bucks in which 4 adults had foodamazed at the speed and process by which they deliver food and in my book this is a must visit when in Delhi ncr <------> Delhi
the Big Brand Bikanerwala in Sec 29 , Gurgaon . <------> Gurgaon
yrs back when i has tasted their Raj Kachodi in a Delhi branch . <------> Delhi
ghewar - have not been able to find it in even popular sweet stores in Chennai . <------> Chennai
kashmiri Laddoo - Oho was the favorite <------> Oho
overall heartyy sweeet 'dinner' for 300 / - Maybe shud go check out their restaurant next time@management - Pls consider opening a branch in Chennai  <------> Chennai
whenever we want to have something not very expensive and something that tastes nice and is authentic Indian , and when in Gurgaon we visit this bikanervala outlet in Gurgaon . <------> Gurgaon Gurgaon
whenever i visit my uncles place who stays in Gurgaon , i make it a point to carry 1 <------> Gurgaon
will keep on coming here whenever will come to Gurgaon . <------> Gurgaon
i have been to Bikanervala of Sector - 29 , Gurgaon thrice . <------> Gurgaon
i had the post exam party at Bromfy . <------> Bromfy
you can have all kinds of parties in Bromfy , whether it be a Post Exam party or a birthday bash or a small get together . <------> Bromfy
this time i found the good lounge in Kamla Nagar. there is lot many <------> Kamla Nagar
^[[B^[[B2       coast cafe is one on our favorite places to eat in Delhi . <------> Delhi
we spent the new years eve 2015 here , and the mulled wine and Moscow mule were exceptionally good . <------> Moscow
fish tacos and malabari cocum curry are the probably the best dishes in Delhi .. <------> Delhi
& nbsp ; Lovely ambience , located above Ogaan , next to Imperfecto building . <------> Ogaan Imperfecto
something i guess i had to struggle to find even in Hyderabad  <------> Hyderabad
had & nbsp ; Malabari Cokum Mixed Veggie Curry with & nbsp ; Malabari Parantha and Appam . <------> Malabari Parantha
go for the Kokum Curry , Moilee , Garam Curry and Stew . <------> Kokum Curry
located just beside Impfercto , coast cafe is classy and exudes understated elegance . <------> Impfercto
while the fried mushrooms were unbearably spicy and inedible beyond a point , chicken curry Kerala style was a clear winner . <------> Kerala
the food is an interesting mix of Malabar / Kerala cuisine with some dashes of Italian and Mexican food . <------> Kerala
this place might just save Hauz Khas Village , for everyone who's sick of having over - priced , below average food , & nbsp ; this is absolutely & nbsp ; refreshing . <------> Hauz Khas Village
the Kerala prawn curry and mutton fry are absolute favourites . <------> Kerala
originally a sweet shop i admire Bikanervala for standing up to the mcdonalds , kfc's and all international food chains in India . <------> India
the Gurgaon restaurant has a play area at the restaurant level for the kids and keeps them busy . <------> Gurgaon
try visiting during the Navratri days and the food is awesome without any onion & amp ; garlic for people who are fasting.askmaverick.wordpress.com <------> Navratri
i'd never seen anything like this before in India , not in Bangalore , Hyderabad or Mumbai . <------> India Bangalore Hyderabad Mumbai
of course because Gurgaon is a planned / modern town it is possible to have such venues . <------> Gurgaon
but then again this part of Gurgaon might as well have been in New Jersey . <------> Gurgaon New Jersey
do go to Bikanerwala <------> Bikanerwala
but more like the Maruti Suzuki , or even a Honda City . <------> Honda City
this is one of the largest eateries in Gurgaon in terms of sheer size . <------> Gurgaon
they serve a good Poori - Subzi - Halwa - Lassi breakfast - good for an inexpensive lazy late breakfast on Sunday after a late Saturday night . <------> Halwa
the Motichoor Ka Laddu ( the one with the highest price ) is one of the best ladoos i had in Gurgaon - It is soft & amp ; juicy & amp ; just melts in mouth & amp ; the sweetness is optimum . <------> Gurgaon
there is a Bengali sweet counter as well which has a few good sweets like Gur Rasmalai , Mishti Doi , Sandesh etc <------> Gur Rasmalai
unlike Haldiram , food quality and menus of Bikanervala restaurants is not standardised . <------> Bikanervala
but this particular Bikanervala is just too good to believe . <------> Bikanervala
i stay in Dwarka , <------> Dwarka
spread across 3 floors and the only Restaurant in Leisure Valley with its own Private Parking ( till 5 pm ) . <------> Leisure Valley
with restaurants , clubs and cafes at every step in Hauz Khas Village this cafe is a fresh breath of air . <------> Hauz Khas Village
the food is genuinely good and serves some of the best coastal variety of foods form across India . <------> India
great authentic Kerala food . <------> Kerala
best i've had outside Kerala ( arguably better than in Kerala as well ) . <------> Kerala Kerala
finally a good place in Delhi for coastal food . <------> Delhi
just came back from Kerala and can confidently say the appams at coast cafe are really good . <------> Kerala
& nbsp ; The quaint interiors here reminded me of a legendary Port Blair restaurant - Pearless . <------> Port Blair
but a good cocktail menu ( ordered the Kafir ) and some of the finest coastal food you can get in Delhi ( i had the fish curry with malabar parantha ) made for a total treat  <------> Delhi
at the very onset Coast Cafe is unusual from other cafes in hkv or even Delhi in part due to its elegant and subtle decor and spacious tables set comfortably apart from each other - unlike many of the cramped cafes one has to endure in the city . <------> Delhi
heck , i enjoyed this place so much it might even convince me to brave the chaotic mess of Hauz Khas Village to eat here more often .... <------> Hauz Khas Village
but Coast Cafe has brought the happiness back with their amazing dishes from Kerala . <------> Kerala

