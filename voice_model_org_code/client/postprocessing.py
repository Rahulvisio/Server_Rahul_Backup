import re
import json

import utility as ed
from word_array import lang_word_data

match_words_hi=lang_word_data['hi']
match_words_mr=lang_word_data['mr']


match_words_39_hi = [item.strip() for item in match_words_hi['39'].split(',') if item.strip()]


match_words_49_hi = [item.strip() for item in match_words_hi['49'].split(',') if item.strip()]


match_words_59_hi = [item.strip() for item in match_words_hi['59'].split(',') if item.strip()]
match_words_69_hi = [item.strip() for item in match_words_hi['69'].split(',') if item.strip()]
match_words_79_hi = [item.strip() for item in match_words_hi['79'].split(',') if item.strip()]
match_words_89_hi = [item.strip() for item in match_words_hi['89'].split(',') if item.strip()]
match_words_67_hi = [item.strip() for item in match_words_hi['67'].split(',') if item.strip()]

# mr section

match_words_19 = [item.strip() for item in match_words_mr['19'].split(',') if item.strip()]
match_words_29 = [item.strip() for item in match_words_mr['29'].split(',') if item.strip()]
match_words_39 = [item.strip() for item in match_words_mr['39'].split(',') if item.strip()]


match_words_49 = [item.strip() for item in match_words_mr['49'].split(',') if item.strip()]


match_words_59 = [item.strip() for item in match_words_mr['59'].split(',') if item.strip()]
match_words_69 = [item.strip() for item in match_words_mr['69'].split(',') if item.strip()]
match_words_79 = [item.strip() for item in match_words_mr['79'].split(',') if item.strip()]
match_words_89 = [item.strip() for item in match_words_mr['89'].split(',') if item.strip()]
match_words_67 = [item.strip() for item in match_words_mr['67'].split(',') if item.strip()]


def gabbar_batch_process(gabbar_generator, audio_files,language='english', task = 'transcribe', batch_size=8):
  
    return gabbar_generator(
            audio_files,
            chunk_length_s=30,
            batch_size=batch_size,
            return_timestamps=False,
            generate_kwargs={"language":language,"task":task}
        )
def remove_zeros(input_list):

    return [item for item in input_list if item.strip('0')]
def extract_number_and_length(text):

    match = re.search(r'\d+', text)
    if match:
        number = match.group(0)
        length_of_number = len(number)
        return number, length_of_number
    else:
        return None, 0
    


def split_hindi_text(hindi_text):

    place_markers = ["लाग","लाथ","लाक","लाख", "हजर","हज़ाड","हदार","हज़ार","हजाड","अजार","जार","सो","सौ","ओ","सहओ","सहूं"]
    

    pattern = r"(.*?(" + "|".join(place_markers) + r"))"
    

    matches = re.findall(pattern, hindi_text)
    
    # Extract the first part of each match (the full group)
    result = [match[0].strip() for match in matches]
    
    # Append any remaining text that doesn’t match the place markers
    remaining_text = re.sub(pattern, "", hindi_text).strip()
    if remaining_text:
        result.append(remaining_text)

    return result

def split_number(number):
    # Ensure the number is a string and pad it to 7 digits
    number_str = str(number).zfill(7)

    # Extract segments: 
    # 1. First part can be the first two digits or the first one and part of the next.
    # 2. The second part consists of the next two digits.
    # 3. The last part is the last two digits.
    part1 = number_str[:2]     # First two digits for part 1
    part2 = number_str[2:5]     # Next three digits for part 2
    part3 = number_str[5:7]    # Last two digits for part 3
    
    val=[part1, part2, part3]
    return remove_zeros(val)
def special_split_number(number):
    number_str = str(number).zfill(7)

    # Extract segments: 
    # 1. First part can be the first two digits or the first one and part of the next.
    # 2. The second part consists of the next two digits.
    # 3. The last part is the last two digits.
    part1 = number_str[:2]     # First two digits for part 1
    part2 = number_str[2:4]     # Next three digits for part 2
    part3 = number_str[4:5]     # Next three digits for part 2
    part4 = number_str[5:7]    # Last two digits for part 3
    
    val=[part1, part2, part3,part4]
    return val
def post_processing_hi(text,hi_gabbar_generator,audio_bytes,gabbar_text):

        text=text.replace(',','')
        number, length_of_number = extract_number_and_length(text)
        number_array=[]
        count=0

        my_text=""

        if "49" in text:
            count = str(number).count("49")

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language='hi')

            my_text=results[0]['text']

            contains_word_39 = any(word in my_text for word in match_words_39_hi)

            
            contains_word_49 = any(word in my_text for word in match_words_49_hi)
   

            if count==1 and contains_word_39 and not contains_word_49 :
 
               gabbar_text=gabbar_text.replace("49","39")
             
           

        elif "40" in text:

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language='hi')
            count = str(number).count("40")

      
            my_text=results[0]['text']

            contains_word = any(word in my_text for word in match_words_39_hi)
   

            if count==1 and  contains_word :
               gabbar_text=gabbar_text.replace("40","39")
              


        if "59" in text:

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language='hi')
            count = str(number).count("59")

            my_text=results[0]['text']
    
            contains_word = any(word in my_text for word in match_words_49_hi)


            if count==1 and contains_word :
               gabbar_text=gabbar_text.replace("59","49")

        if "69" in text:
            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language='hi')
            count = str(number).count("69")

            my_text=results[0]['text']

            contains_word = any(word in my_text for word in match_words_59_hi)

            if count==1 and contains_word :
               gabbar_text=gabbar_text.replace("69","59")

        if "79" in text:

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language='hi')
            count = str(number).count("79")
   
            my_text=results[0]['text']


            contains_word = any(word in my_text for word in match_words_69_hi)

            if count==1 and contains_word :
               gabbar_text=gabbar_text.replace("79","69")
        if "89" in text:

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language='hi')
            count = str(number).count("89")
 
            my_text=results[0]['text']


            contains_word = any(word in my_text for word in match_words_79_hi)
  
            if count==1 and contains_word :
               gabbar_text=gabbar_text.replace("89","79")
        if "60" in text:

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language='hi')
            count = str(number).count("60")
    
            my_text=results[0]['text']


            contains_word = any(word in my_text for word in match_words_67_hi)
   
            if count==1 and contains_word :
               gabbar_text=gabbar_text.replace("60","67")
        if "65" in text:

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language='hi')
            count = str(number).count("65")
    
            my_text=results[0]['text']


            contains_word = any(word in my_text for word in match_words_67_hi)

            if count==1 and contains_word :
               gabbar_text=gabbar_text.replace("65","67")
        if "68" in text:

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language='hi')
            count = str(number).count("68")
    
            my_text=results[0]['text']


            contains_word = any(word in my_text for word in match_words_67_hi)
           
            if count==1 and contains_word :
               gabbar_text=gabbar_text.replace("68","67")

        if count>1:
           if "49" or "40" or "69" or "79" or "89" or "60" or "65" or "66"  in text:

            if my_text !="भारती रुपीज":

               hindi_array=split_hindi_text(my_text)
               text=text.replace(',','')
           
               number, length_of_number = extract_number_and_length(text)
  
               number_array=split_number(number)

            enter_into_for_loop=True
            if length_of_number==4 or length_of_number==5:

                if len(hindi_array)==3 and len(number_array)==2:
                   if "49" in text:
                        contains_word1 = any(word in hindi_array[0] for word in match_words_39_hi)
                        contains_word2 = any(word in hindi_array[2] for word in match_words_39_hi)
                        contains_word3 = any(word in hindi_array[0] for word in match_words_49_hi)
                        contains_word4 = any(word in hindi_array[2] for word in match_words_49_hi)
         
                        if contains_word1 and not contains_word3 :
                           number_array[0]= number_array[0].replace("49","39")
                        if contains_word2 and not contains_word4 :
                           number_array[1]= number_array[1].replace("49","39")
                        enter_into_for_loop=False
                   if "40" in text:
                        contains_word1 = any(word in hindi_array[0] for word in match_words_39_hi)
                        contains_word2 = any(word in hindi_array[2] for word in match_words_39_hi)
                        if contains_word1 :
                           number_array[0]= number_array[0].replace("40","39")
                        if contains_word2 :
                           number_array[1]= number_array[1].replace("40","39")
                        enter_into_for_loop=False
                   if "69" in text:
                        contains_word1 = any(word in hindi_array[0] for word in match_words_59_hi)
                        contains_word2 = any(word in hindi_array[2] for word in match_words_59_hi)
                        if contains_word1 :
                           number_array[0]= number_array[0].replace("69","59")
                        if contains_word2 :
                           number_array[1]= number_array[1].replace("69","59")
                        enter_into_for_loop=False
                   if "79" in text:
                        contains_word1 = any(word in hindi_array[0] for word in match_words_69_hi)
                        contains_word2 = any(word in hindi_array[2] for word in match_words_69_hi)
                        if contains_word1 :
                           number_array[0]= number_array[0].replace("79","69")
                        if contains_word2 :
                           number_array[1]= number_array[1].replace("79","69")
                        enter_into_for_loop=False
                   if "89" in text:
                        contains_word1 = any(word in hindi_array[0] for word in match_words_79_hi)
                        contains_word2 = any(word in hindi_array[2] for word in match_words_79_hi)
                        if contains_word1 :
                           number_array[0]= number_array[0].replace("89","79")
                        if contains_word2 :
                           number_array[1]= number_array[1].replace("89","79")
                   if "60" in text:
                        contains_word1 = any(word in hindi_array[0] for word in match_words_67_hi)
                        contains_word2 = any(word in hindi_array[2] for word in match_words_67_hi)
                        if contains_word1 :
                           number_array[0]= number_array[0].replace("60","67")
                        if contains_word2 :
                           number_array[1]= number_array[1].replace("60","67")
                        enter_into_for_loop=False
                   if "65" in text:
                        contains_word1 = any(word in hindi_array[0] for word in match_words_67_hi)
                        contains_word2 = any(word in hindi_array[2] for word in match_words_67_hi)
                        if contains_word1 :
                           number_array[0]= number_array[0].replace("65","67")
                        if contains_word2 :
                           number_array[1]= number_array[1].replace("65","67")
                        enter_into_for_loop=False
                   if "66" in text:
                        contains_word1 = any(word in hindi_array[0] for word in match_words_67_hi)
                        contains_word2 = any(word in hindi_array[2] for word in match_words_67_hi)
                        if contains_word1 :
                           number_array[0]= number_array[0].replace("66","67")
                        if contains_word2 :
                           number_array[1]= number_array[1].replace("66","67")
                        enter_into_for_loop=False
             
            elif length_of_number>=6:
                number_array=special_split_number(number)

            temp=0
            if enter_into_for_loop:
             for i in range(len(number_array)):
              temp=temp+1

              j=i

              if "49" in number_array[i]:
       
                if len(hindi_array)==1:
             
                    j=0
                
                elif i>=len(hindi_array):
                    break
     
                contains_word_39 = any(word in hindi_array[j] for word in match_words_39_hi)
                contains_word_49 = any(word in hindi_array[j] for word in match_words_49_hi)
               
                if contains_word_39 and not contains_word_49 :
                   number_array[j]= number_array[j].replace("49","39")
                            
              if "40" in number_array[i]:
          
                            
                if len(hindi_array)==1:
             
                    j=0
                
                elif i>=len(hindi_array):
                    break
              
                contains_word = any(word in hindi_array[j] for word in match_words_39_hi)
      
                if contains_word :
                     number_array[i]= number_array[i].replace("40","39")
              if "59" in number_array[i]:
        
         
                if len(hindi_array)==1:
             
                    j=0
                
                elif i>=len(hindi_array):
                    break
        
                contains_word = any(word in hindi_array[j] for word in match_words_59_hi)
  
                if contains_word:
                   number_array[i]= number_array[i].replace("59","49")

              if "69" in number_array[i]:
              
                         
                if len(hindi_array)==1:
             
                    j=0
                
                elif i>=len(hindi_array):
                    break
              
                contains_word = any(word in hindi_array[j] for word in match_words_59_hi)
               
                if contains_word:
                   number_array[i]= number_array[i].replace("69","59")
              if "79" in number_array[i]:
 
                if len(hindi_array)==1:
             
                    j=0
                
                elif i>=len(hindi_array):
                    break
         
                contains_word = any(word in hindi_array[j] for word in match_words_69_hi)

                if contains_word:
                   number_array[i]= number_array[i].replace("79","69")
              if "89" in number_array[i]:
           
                         
                if len(hindi_array)==1:
             
                    j=0
                
                elif i>=len(hindi_array):
                    break
                
                contains_word = any(word in hindi_array[j] for word in match_words_69_hi)
 
                if contains_word:
                   number_array[i]= number_array[i].replace("89","79")
              if "80" in number_array[i]:
  
                         
                if len(hindi_array)==1:
             
                    j=0
                
                elif i>=len(hindi_array):
                    break
               
                contains_word = any(word in hindi_array[j] for word in match_words_69_hi)
             
                if contains_word:
                   number_array[i]= number_array[i].replace("80","89")
              if "180" in number_array[i]:
               
                         
                if len(hindi_array)==1:
             
                    j=0
                
                elif i>=len(hindi_array):
                    break
               
                contains_word = any(word in hindi_array[j] for word in match_words_69_hi)

                if contains_word:
                   number_array[i]= number_array[i].replace("180","89")
              if "980" in number_array[i]:
                    
                if len(hindi_array)==1:
             
                    j=0
                
                elif i>=len(hindi_array):
                    break
               
                contains_word = any(word in hindi_array[j] for word in match_words_69_hi)
         
                if contains_word:
                   number_array[i]= number_array[i].replace("980","89")
              if "60" in number_array[i]:
              
                if len(hindi_array)==1:
             
                    j=0
                
                elif i>=len(hindi_array):
                    break
 
                contains_word = any(word in hindi_array[j] for word in match_words_69_hi)
    
                if contains_word:
                   number_array[i]= number_array[i].replace("60","67")
              if "65" in number_array[i]:
      
                         
                if len(hindi_array)==1:
             
                    j=0
                
                elif i>=len(hindi_array):
                    break
          
                contains_word = any(word in hindi_array[j] for word in match_words_69_hi)
             
                if contains_word:
                   number_array[i]= number_array[i].replace("60","67")
              if "66" in number_array[i]:
         
                         
                if len(hindi_array)==1:
             
                    j=0
                
                elif i>=len(hindi_array):
                    break
         
                contains_word = any(word in hindi_array[j] for word in match_words_69_hi)
     
                if contains_word:
                   number_array[i]= number_array[i].replace("66","67")
              
           modify_number_str=''.join(number_array)

           text=text.replace(str(number),modify_number_str)
           gabbar_text=text
        

        return gabbar_text   
        

def post_processing_mr(text,hi_gabbar_generator,audio_bytes,gabbar_text,lang='mr'):
        text=text.replace(',','')
        number, length_of_number = extract_number_and_length(text)
        number_array=[]
        count=0

        my_text=""

        if "1.20" in text:

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language=lang)
         
      
            my_text=results[0]['text']

            contains_word_19 = any(word in my_text for word in match_words_19)
  

            if contains_word_19:
 
                 gabbar_text=gabbar_text.replace("1.20","19")
             
        if "1.29" in text:

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language=lang)
      
            my_text=results[0]['text']

            contains_word_19 = any(word in my_text for word in match_words_19)
    

            if contains_word_19:
 
                 gabbar_text=gabbar_text.replace("1.29","19")
        if "199" in text:

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language=lang)

            my_text=results[0]['text']

            contains_word_19 = any(word in my_text for word in match_words_19)


            if contains_word_19:
 
                 gabbar_text=gabbar_text.replace("199","19")
        if "29" in text:

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language=lang)
            count = str(number).count("29")
         
            my_text=results[0]['text']

            contains_word_19 = any(word in my_text for word in match_words_19)
      

            if count==1 and  contains_word_19:
 
                 gabbar_text=gabbar_text.replace("29","19")
             
        if "21" in text:

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language=lang)

            count = str(number).count("21")
            my_text=results[0]['text']

            contains_word_19 = any(word in my_text for word in match_words_19)


            if count==1 and contains_word_19:
 
                 gabbar_text=gabbar_text.replace("21","19")
        if "31" in text:

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language=lang)
            count = str(number).count("31")

            my_text=results[0]['text']

            contains_word = any(word in my_text for word in match_words_29)


            if count==1 and  contains_word:
 
                 gabbar_text=gabbar_text.replace("31","29")
        if "41" in text:

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language=lang)
            count = str(number).count("41")

            my_text=results[0]['text']

            contains_word = any(word in my_text for word in match_words_39)


            if count==1 and contains_word:
 
                 gabbar_text=gabbar_text.replace("41","39")
        if "49" in text:

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language=lang)
            count = str(number).count("49")
    
            my_text=results[0]['text']

            contains_word = any(word in my_text for word in match_words_39)


            if count==1 and contains_word:
 
                 gabbar_text=gabbar_text.replace("49","39")
        if "150" in text:

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language=lang)

            my_text=results[0]['text']

            contains_word = any(word in my_text for word in match_words_49)


            if contains_word:
 
                 gabbar_text=gabbar_text.replace("150","49")
        if "60" in text:

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language=lang)
            count = str(number).count("60")

            my_text=results[0]['text']

            contains_word = any(word in my_text for word in match_words_59)


            if count==1 and  contains_word:
 
                 gabbar_text=gabbar_text.replace("60","59")
        if "61" in text:

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language=lang)
            count = str(number).count("61")
         
            my_text=results[0]['text']

            contains_word = any(word in my_text for word in match_words_59)
 

            if count and contains_word:
 
                 gabbar_text=gabbar_text.replace("61","59")


        if "69" in text:

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language=lang)
            count = str(number).count("69")

            my_text=results[0]['text']

            contains_word = any(word in my_text for word in match_words_59)
   

            if count==1 and  contains_word:
 
                 gabbar_text=gabbar_text.replace("69","59")



        if "79" in text:

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language=lang)
            count = str(number).count("79")
      
            my_text=results[0]['text']

            contains_word = any(word in my_text for word in match_words_69)
     

            if count==1 and contains_word:
 
                 gabbar_text=gabbar_text.replace("79","69")
        if "71" in text:

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language=lang)
            count = str(number).count("71")
        
            my_text=results[0]['text']

            contains_word = any(word in my_text for word in match_words_69)
       

            if count==1 and contains_word:
 
                 gabbar_text=gabbar_text.replace("71","69")




        if "89" in text:

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language=lang)
            count = str(number).count("89")
       
            my_text=results[0]['text']

            contains_word = any(word in my_text for word in match_words_79)
    

            if  count==1 and contains_word:
 
                 gabbar_text=gabbar_text.replace("89","79")
        if "99" in text:

            results=gabbar_batch_process(hi_gabbar_generator,audio_bytes,language=lang)
            count = str(number).count("99")
        
            my_text=results[0]['text']

            contains_word = any(word in my_text for word in match_words_89)
  

            if count and contains_word:
 
                 gabbar_text=gabbar_text.replace("99","79")



        if count>1:
           if "21" or "29" or "31" or "41" or "49" or "150" or "60" or "61" or "71" or "79" or "89" or "99" in text:

            if my_text !="भारती रुपीज":

               hindi_array=split_hindi_text(my_text)
               text=text.replace(',','')
     
               number, length_of_number = extract_number_and_length(text)
               
               number_array=split_number(number)

          

            enter_into_for_loop=True
            if length_of_number==4 or length_of_number==5:

                if len(hindi_array)==3 and len(number_array)==2:
                   if "21" in text:
                        contains_word1 = any(word in hindi_array[0] for word in match_words_19)
                        contains_word2 = any(word in hindi_array[2] for word in match_words_19)
                        if contains_word1 :
                           number_array[0]= number_array[0].replace("21","19")
                        if contains_word2 :
                           number_array[1]= number_array[1].replace("21","19")
                        enter_into_for_loop=False
                   if "29" in text:
                        contains_word1 = any(word in hindi_array[0] for word in match_words_19)
                        contains_word2 = any(word in hindi_array[2] for word in match_words_19)
                        if contains_word1 :
                           number_array[0]= number_array[0].replace("29","19")
                        if contains_word2 :
                           number_array[1]= number_array[1].replace("29","19")
                   if "31" in text:
                        contains_word1 = any(word in hindi_array[0] for word in match_words_29)
                        contains_word2 = any(word in hindi_array[2] for word in match_words_29)
                        if contains_word1 :
                           number_array[0]= number_array[0].replace("31","29")
                        if contains_word2 :
                           number_array[1]= number_array[1].replace("31","29")
                   if "41" in text:
                        contains_word1 = any(word in hindi_array[0] for word in match_words_29)
                        contains_word2 = any(word in hindi_array[2] for word in match_words_29)
                        if contains_word1 :
                           number_array[0]= number_array[0].replace("41","39")
                        if contains_word2 :
                           number_array[1]= number_array[1].replace("41","39")
                        enter_into_for_loop=False
                   if "49" in text:
                        contains_word1 = any(word in hindi_array[0] for word in match_words_29)
                        contains_word2 = any(word in hindi_array[2] for word in match_words_29)
                        if contains_word1 :
                           number_array[0]= number_array[0].replace("49","39")
                        if contains_word2 :
                           number_array[1]= number_array[1].replace("49","39")
                        enter_into_for_loop=False
                   if "79" in text:
                        contains_word1 = any(word in hindi_array[0] for word in match_words_69)
                        contains_word2 = any(word in hindi_array[2] for word in match_words_69)
                        if contains_word1 :
                           number_array[0]= number_array[0].replace("79","69")
                        if contains_word2 :
                           number_array[1]= number_array[1].replace("79","69")
                        enter_into_for_loop=False
                   if "71" in text:
                        contains_word1 = any(word in hindi_array[0] for word in match_words_69)
                        contains_word2 = any(word in hindi_array[2] for word in match_words_69)
                        if contains_word1 :
                           number_array[0]= number_array[0].replace("71","69")
                        if contains_word2 :
                           number_array[1]= number_array[1].replace("71","69")
                        enter_into_for_loop=False 

                   if "89" in text:
                        contains_word1 = any(word in hindi_array[0] for word in match_words_79)
                        contains_word2 = any(word in hindi_array[2] for word in match_words_79)
                        if contains_word1 :
                           number_array[0]= number_array[0].replace("89","79")
                        if contains_word2 :
                           number_array[1]= number_array[1].replace("89","79")

                   if "99" in text:
                        contains_word1 = any(word in hindi_array[0] for word in match_words_79)
                        contains_word2 = any(word in hindi_array[2] for word in match_words_79)
                        if contains_word1 :
                           number_array[0]= number_array[0].replace("99","79")
                        if contains_word2 :
                           number_array[1]= number_array[1].replace("99","79")


                   if "60" in text:
                        contains_word1 = any(word in hindi_array[0] for word in match_words_59)
                        contains_word2 = any(word in hindi_array[2] for word in match_words_59)
                        if contains_word1 :
                           number_array[0]= number_array[0].replace("60","59")
                        if contains_word2 :
                           number_array[1]= number_array[1].replace("60","59")
                        enter_into_for_loop=False
                   if "61" in text:
                        contains_word1 = any(word in hindi_array[0] for word in match_words_59)
                        contains_word2 = any(word in hindi_array[2] for word in match_words_59)
                        if contains_word1 :
                           number_array[0]= number_array[0].replace("61","59")
                        if contains_word2 :
                           number_array[1]= number_array[1].replace("61","59")
                        enter_into_for_loop=False
                   if "69" in text:
                        contains_word1 = any(word in hindi_array[0] for word in match_words_59)
                        contains_word2 = any(word in hindi_array[2] for word in match_words_59)
                        if contains_word1 :
                           number_array[0]= number_array[0].replace("69","59")
                        if contains_word2 :
                           number_array[1]= number_array[1].replace("69","59")
                        enter_into_for_loop=False

            elif length_of_number>=6:
                number_array=special_split_number(number)

            temp=0
            if enter_into_for_loop:
             for i in range(len(number_array)):
              temp=temp+1
  
              j=i

              if "21" in number_array[i]:

                if len(hindi_array)==1:
             
                    j=0
                
                elif i>=len(hindi_array):
                    break
  
                contains_word = any(word in hindi_array[j] for word in match_words_19)
        
 
                if contains_word:
                   number_array[j]= number_array[j].replace("21","19")
               
              if "29" in number_array[i]:

                if len(hindi_array)==1:
             
                    j=0
                
                elif i>=len(hindi_array):
                    break

                contains_word = any(word in hindi_array[j] for word in match_words_19)
        
   
                if contains_word:
                   number_array[j]= number_array[j].replace("29","19")
              if "31" in number_array[i]:
 
                if len(hindi_array)==1:
             
                    j=0
                
                elif i>=len(hindi_array):
                    break

                contains_word = any(word in hindi_array[j] for word in match_words_29)
        
                if contains_word:
                   number_array[j]= number_array[j].replace("31","29")
              if "41" in number_array[i]:
  
                if len(hindi_array)==1:
             
                    j=0
                
                elif i>=len(hindi_array):
                    break

                contains_word = any(word in hindi_array[j] for word in match_words_39)
        

                if contains_word:
                   number_array[j]= number_array[j].replace("41","39")

              if "40" in number_array[i]:

                if len(hindi_array)==1:
             
                    j=0
                
                elif i>=len(hindi_array):
                    break
     
                contains_word = any(word in hindi_array[j] for word in match_words_39)

                if contains_word :
                     number_array[i]= number_array[i].replace("40","39")



              if "69" in number_array[i]:

                         
                if len(hindi_array)==1:
             
                    j=0
                
                elif i>=len(hindi_array):
                    break

                contains_word = any(word in hindi_array[j] for word in match_words_59)
       
                if contains_word:
                   number_array[i]= number_array[i].replace("69","59")
              if "79" in number_array[i]:
          
                         
                if len(hindi_array)==1:
             
                    j=0
                
                elif i>=len(hindi_array):
                    break

                contains_word = any(word in hindi_array[j] for word in match_words_69)

                if contains_word:
                   number_array[i]= number_array[i].replace("79","69")

              if "71" in number_array[i]:
  
                if len(hindi_array)==1:

                    j=0

                elif i>=len(hindi_array):
                    break
   
                contains_word = any(word in hindi_array[j] for word in match_words_69)
  
                if contains_word:
                   number_array[i]= number_array[i].replace("71","69")

              if "89" in number_array[i]:
 
                if len(hindi_array)==1:
             
                    j=0
                
                elif i>=len(hindi_array):
                    break
       
                contains_word = any(word in hindi_array[j] for word in match_words_79)

                if contains_word:
                   number_array[i]= number_array[i].replace("89","79")


              if "99" in number_array[i]:


                if len(hindi_array)==1:

                    j=0

                elif i>=len(hindi_array):
                    break
        
                contains_word = any(word in hindi_array[j] for word in match_words_79)

                if contains_word:
                   number_array[i]= number_array[i].replace("99","79")



              if "60" in number_array[i]:
     
                         
                if len(hindi_array)==1:
             
                    j=0
                
                elif i>=len(hindi_array):
                    break
   
                contains_word = any(word in hindi_array[j] for word in match_words_59)

                if contains_word:
                   number_array[i]= number_array[i].replace("60","59")
              if "61" in number_array[i]:

                         
                if len(hindi_array)==1:
             
                    j=0
                
                elif i>=len(hindi_array):
                    break
     
                contains_word = any(word in hindi_array[j] for word in match_words_59)

                if contains_word:
                   number_array[i]= number_array[i].replace("60","59")
              if "69" in number_array[i]:
      
                         
                if len(hindi_array)==1:

                    j=0
                
                elif i>=len(hindi_array):
                    break
             
                contains_word = any(word in hindi_array[j] for word in match_words_59)
    
                if contains_word:
                   number_array[i]= number_array[i].replace("69","59")              
           modify_number_str=''.join(number_array)

           text=text.replace(str(number),modify_number_str)
           gabbar_text=text


        return gabbar_text
