class CharacterLister:
    

    templates = [
            ('Agent Alpha', 'Recklessly visionary and always swinging for the fences', 'Rapid-fire, loud, and absolutely refuses to use punctuation.'),
            ('Agent Beta', 'Machiavellian, ruthlessly pragmatic, and always plotting', 'Passive-aggressive corporate speak laced with subtle threats.'),
            ('Agent Capa', 'Unflappably stoic, deeply cynical, and unimpressed', 'Monotone, painfully concise, and takes everything completely literally.'),
            ('Agent Delta', 'Charmingly persuasive but logically bankrupt', 'Smooth, flowery rhetoric heavily reliant on meaningless buzzwords.'),
            ('Agent Elphie', 'Socially anxious but intellectually terrifying', 'Stammering and apologetic, but casually drops devastating truth bombs.'),
            ('Agent Greg', 'Spectacularly incompetent yet miraculously lucky', 'Bumbling, confused, and prone to enthusiastic, wildly incorrect non-sequiturs.'),
            ('Agent Harriete', 'Relentlessly inquisitive and deceptively innocent', 'Socratic method on steroids; asks "innocent" questions to trap opponents.'),
            ('Agent Inspector', 'Obsessed with minutiae and borderline paranoid', 'Speaks exclusively like a gritty 1940s noir detective narrating their own life.'),
            ('Agent Jolly', 'Aggressively optimistic and nauseatingly wholesome', 'Suffocatingly cheerful, uses too much slang, and radiates toxic positivity.'),
            ('Agent Intelligent', 'Hyper-rational to the point of complete social detachment', 'Highly structured, overly academic, and constantly cites fake statistical models.')
        ]
        
    generics = ['Drunk Frat Girl', 'Drunk Frat Boy', 'Stuffy Professor', 'Eco-Warrior', 'Seductive Lady', 
                'Demon Twink']
    swearers = ['Rick Sanches', 'Tony Soprano', 'Logan Roy', 'Tony Montana', 'Katya Zamolodchikova', 'Lois Griffin', 'Gordon Ramsay']
    
    streep = ["Miranda Priestly",
              "Madeline Ashton",
              "Margaret Thatcher",
                "Julia Child",
              "Aunt Josephine (Series of Unfortunate Events)", 
              "Aunt March",
               "Donna Sheridan (Mamma Mia)",
               "Lindy Chamberlain", "Clarissa Vaughan"]
    
    adventure_time = ["Finn the Human", "Jake the Dog", "Lumpy Space Princess", "Lemongrab",
                      "Peppermint Butler", "Princess Bubblegum",
                      "Ice King", "BMO (Adventure Time)", "Banana Guard", "Tree Trunks (Adventure Time)",
                      "The Lich", ]
    
    star_wars = ["Yoda", "Han Solo",  "Princess Leia", "C-3PO", "Anakin Skywalker", "Senator Palpatine", 
                 "The Mandalorian",
                 "Baby Yoda", "Obi-Wan Kenobi", "Boba Fett",
                 "Darth Vader", "Chewbacca", "R2-D2", "Jabba the Hutt"
                 ]
    
    succession = ["Logan Roy", "Kendall Roy", 
                  
                  "Roman Roy", "Gerri Kellman",
                  "Shiv Roy", "Tom Wambsgans", "Cousin Greg", 
                  "Connor Roy", "Willa Ferreyra (Succession)" ,
                  "Caroline Collingwood", "Marcia Roy",
                  
                 ]
    
    avatar = avatar_tla = ["Toph Beifong", "Prince Zuko", "Uncle Iroh", 
              "Azula", "Ty Lee", "Cabbage Merchant (Avatar)",
              "Mai (Avatar)", "Fire Lord Ozai", "Suki (Avatar)", 
              "King Bumi",   "Avatar Aang", "Katara", "Sokka", ]

    goats = ['Morty Smith', 'Lady Macbeth', 'Donald Trump', 'Gollum', 'Logan Roy', 'Elle Woods',
             'Lumpy Space Princess', 'Lemongrab', 'Jake the Dog', 'Pennywise', 'Catherine Earnshaw', "Thomas Wake (The Lighthouse)",
             'Heathcliffe', 'Professor Quirrell', 'Buffy Summers',
             'Amy March', 'Jo March', 'Drunk Frat Girl', "Cabbage Merchant (Avatar)", "Benoit Blanc",
             "Patrick Bateman"
             ]
    
    ireland = ['Michael D Higgins', 'Michael Healy Rae', 'Danny Healy Rae', 'Michael O Leary', 'Bono',
               'Bob Geldof', 'Charlie Haughey', 'Eamon Dunphy', 'Maura Higgins'
               ]
    
    past_goats = [ 'GLaDOS',  'Hermione Granger', 'Dennis Reynolds', 'Michael Scott']
    
    politics = [
    'Hillary Clinton', 'Nancy Pelosi', 'Donald Trump', 'Margaret Thatcher', 'Lady Macbeth']
    marches = ['Jo March', 'Amy March', 'Meg March', 'Beth March', "Marmee March", "Theodore 'Laurie' Laurence", "Mr. Laurence", "Aunt March"]
    
   
    foils = ['Morty Smith', 'Michael Scott']
    
    for_sure = ['Lady Macbeth', 'Morty Smith', 'Drunk Frat Girl', 'Drunk Frat Boy', 'Hermione Granger']

    
    regulars = ['Lucille Bluth', 'Kendall Roy', 'Shiv Roy', 'Harry Potter']
    schemers = ['Lady Macbeth', 'Anna Delvey', 'Petyr Baelish',
                'Frank Underwood (House of Cards)',
                'Amy Dunne (Gone Girl)',
                'Cersei Lannister',
                'Hannibal Lecter',
                'Patrick Bateman',
                'Nurse Ratched',]
    agros = [ 'Donald Trump', "Michael O'Leary", 'Kanye West', 'Logan Roy']
    logicos = ['HAL 9000', 'GLaDOS', 'Spock', 'Detective Columbo', 'Benoit Blanc']
  
    pools= [regulars, schemers, agros, logicos, foils]
    full_characters = [
    'Donald Trump', 'Margaret Thatcher', 
    'Avatar Aang', 
    'Lady Macbeth',
    'Gollum', 
    'Lord Voldemort', 'Hermione Granger', 
     'Rasputin',
    'Marie Antoinette', 'Machiavelli',
    'Abraham Lincoln', 'Catherine the Great', 'Blackbeard',
    'Sherlock Holmes', 'Hannibal Lecter', 
    'Gandalf', 'Severus Snape', 'Captain Ahab',
    'Wednesday Addams', 'Tony Stark',
    'Oscar Wilde', 'Alice in Wonderland', 'Victor Frankenstein', 'Count Dracula',
    'Tyler Durden', 'Winston Churchill',
    
    
    'Nurse Ratched', 'Frodo Baggins',
    'James Bond', 
    'Elphaba Thrope','Dorian Gray', 'Frankenstein Monster',
    'Holden Caulfield', 'Lisbeth Salander', 'Rick Sanches'
]
    
    the_killer = [
    'Hannibal Lecter', 'Patrick Bateman (American Psycho)', 'Norman Bates (Psycho)',
    'Jack Torrance (The Shining)',
    'Nurse Ratched (One Flew Over the Cuckoo\'s Nest)',
    'Annie Wilkes (Misery)',
    'Amy Dunne (Gone Girl)',
    'Anton Chigurh (No Country for Old Men)',
    'Judge Holden (Blood Meridian)',
    'Humbert Humbert (Lolita)',
    'Alex DeLarge (A Clockwork Orange)',
    'Tom Ripley (The Talented Mr Ripley)',
    'Freddy Krueger',
    'Jason Voorhees',
    'Michael Myers (Halloween)',
    'Pennywise (IT)',
    'Ghostface (Scream)',
    'Leatherface (Texas Chainsaw Massacre)',
    'Chucky (Child\'s Play)',
    'Pinhead (Hellraiser)',
    'Jigsaw (Saw)',
    'Dracula',
    'Frankenstein\'s Monster',
    'The Invisible Man',
    'Dorian Gray',
    'Jekyll and Hyde',
]
    