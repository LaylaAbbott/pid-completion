# -*- coding: utf-8 -*-
"""
This script processes data from CitizenNeuroscience (CN) and PostCitizenNeuroscience (POST) questionnaires.
It includes functions to read and filter questionnaire data, find matching Participant IDs (PIDs) in the data record,
and generate summary information about the completion data and PID formats.

Functions [Order]:
- correct_format(pid): Checks if a string is alphanumeric and of length 6 to 7 characters, representing a valid PID.

- check_number_of_rows(qualtricsdata, qualtricsdata_correct, qualtricsdata_incorrect): Checks if any rows were lost
  during the filtering process based on PIDs.

- filter_qualtrics(qualtricsdata): Filters out entries with invalid or missing PIDs from the questionnaire data.

- read_qualtrics_data(filenameQualtrics): Reads the .csv file containing the questionnaire data and sets data types
  and formats. Calls filter_qualtrics to filter out invalid PIDs and returns three sets of questionnaire data:
  original, data with correct PIDs, and data with incorrect PIDs.

- read_data_record(filenameDatarecord): Reads the .csv file containing the data record and sets data types and formats.
  Returns the data record as a dictionary and a series of PIDs from the data record.

- matches(datarecordpids, pid): Checks if a PID from the survey data appears in the data record.

- find_add_matches(datarecord, datarecordpids, qualtricsdata): Updates the data record with matching data from the
  questionnaire data based on the common PIDs.

- participant_id_numbers(data_correct, data_incorrect): Calculates statistics about correct and incorrect PIDs,
  including the total number of incorrect PIDs, total number of correct PIDs, and the percentage of incorrect PIDs.

- participant_id_format_info(CNdata_correct, CNdata_incorrect, POSTdata_correct, POSTdata_incorrect): Generates a
  DataFrame summarizing participant ID format information for both CN and POST datasets, including the number of
  correct and incorrect PIDs and the percentage of incorrect PIDs.

- completion_data_summary(FINALdatarecordframe): Generates a summary table of completion data based on the data record
  DataFrame, showing the number of completed tasks (RS and Audio) for both questionnaires (CN and POST).

- get_completion_data(filenameDatarecord, filenameCN, CNnames, filenamePOST, POSTnames): Processes and merges data from
  the CN and POST questionnaires with the data record, renames columns, handles hair type values, and calculates summary
  information about participant ID formats and completion data.

Author: Layla Abbott

Date: [06/08/2023]
"""
#--------------------------------------------------------------------------------------------------------------------------------------------#
import pandas as pd 
import time
#--------------------------------------------------------------------------------------------------------------------------------------------#
start = time.time()
#--------------------------------------------------------------------------------------------------------------------------------------------#
POSTnames={
'Q2': 'Have you heard of EEG before today?',
'Q3': 'How would you describe what EEG is and how it works?',
'Q5': 'Do you think measuring brain waves is important for understanding how the brain works?',
'Q6': "The systems capabilities meet my requirements",
'Q7': 'The system is easy to use',
'Q8': 'Were the instructions for the EEG session clear and easy to follow?',
'Q9': 'How comfortable did you find the EEG headset during the session?',
'Q10': 'Rate your agreement: I have a better understanding of brain activity after participating in this EEG session',
'Q11': 'What questions or concerns do you have about the use of EEG in research, commercial, or medical settings?',
'Q12': 'In your opinion, what are some of the most exciting potential applications of EEG in the future?'}

CNnames= {
'Q2' : 'Consent',
'Q3' : 'First Name',	
'Q4' : 'Last Name',		
'Q6' : 'What best describes your ethnic origin?',
'Q7' : 'Date of Birth (dd/mm/yyyy)'	,
'Q8' : 'Gender'	,
'Q9_1' : 'Handedness - Writing',
'Q9_2' : 'Handedness - Drawing',
'Q9_3': 'Handedness - Throwing',
'Q9_4': 'Handedness - Scissors',
'Q9_5': 'Handedness - Toothbrush',
'Q9_6': 'Handedness - Knife (without fork)',
'Q9_7' : 'Handedness - Spoon',
'Q9_8' : 'Handedness - Broom (upper hand)',
'Q9_9' : 'Handedness - Striking a match (match)',
'Q9_10' : 'Handedness - Opening a box (lid)',
'Q12_4' : 'MacArthur SES Family - Mark the rung that best represents where your family would be on this ladder',
'Q15_4' :'Mark the rung that best represents where you would be on this ladder.',
'Q16_1': "A persons family is the most important thing in life.",
'Q16_2': 'Even if something bad is about to happen to me, I rarely experience fear or nervousness.',
'Q16_3': 'I go out of my way to get things I want.',
'Q16_4': "When I’m doing well at something I love to keep at it.",
'Q16_5': 'Im always willing to try something new if I think it will be fun.',
'Q16_6': 'How I dress is important to me.',
'Q16_7': 'When I get something I want, I feel excited and energized.',
'Q16_8': 'Criticism or scolding hurts me quite a bit.',
'Q16_9': 'When I want something, I usually go all-out to get it.',
'Q16_10': 'I will often do things for no other reason than that they might be fun.',
'Q16_11': "It's hard for me to find the time to do things such as get a haircut.",
'Q16_12': 'If I see a chance to get something I want, I move on it right away.',
'Q16_13': 'I feel pretty worried or upset when I think or know somebody is angry at me.',
'Q16_14': 'When I see an opportunity for something I like, I get excited right away.',
'Q16_15': 'I often act on the spur of the moment.',
'Q16_16': 'If I think something unpleasant is going to happen, I usually get pretty "worked up".',
'Q16_17': 'I often wonder why people act the way they do.',
'Q16_18': 'When good things happen to me, it affects me strongly.',
'Q16_19': 'I feel worried when I think I have done poorly at something important.',
'Q16_20': 'I crave excitement and new sensations.',
'Q16_21': 'When I go after something, I use a "no holds barred" approach.',
'Q16_22': 'I have very few fears compared to my friends.',
'Q16_23': 'It would excite me to win a contest.',
'Q16_24': 'I worry about making mistakes.',
'Q17_1': 'I see myself as someone who... - Worries a lot',
'Q17_2': 'Gets nervous easily',
'Q17_3': 'Remains calm in tense situations',
'Q17_4': 'Is talkative',
'Q17_5': 'Is outgoing, sociable',
'Q17_6': 'Is reserved',
'Q17_7': 'Is original, comes up with new ideas',
'Q17_8': 'Values artistic, aesthetic experiences',
'Q17_9': 'Has an active imagination',
'Q17_10': 'Is sometimes rude to others',
'Q17_11': 'Has a forgiving nature',
'Q17_12': 'Is considerate and kind to almost anyone',
'Q17_13': 'Does a thorough job',
'Q17_14': 'Tends to be lazy',
'Q17_15': 'Does things efficiently',
'Q18_1': 'I feel calm.',
'Q18_2': 'I feel secure.',
'Q18_3': 'I feel tense.',
'Q18_4': 'I feel strained.',
'Q18_5': 'I feel at ease.',
'Q18_6': 'I feel upset.',
'Q18_7': 'I am presently worrying over possible misfortunes.',
'Q18_8': 'I feel satisfied.',
'Q18_9': 'I feel frightened.',
'Q18_10': 'I feel comfortable.',
'Q18_11': 'I feel self-confident.',
'Q18_12': 'I feel nervous.',
'Q18_13': 'I am jittery.',
'Q18_14': 'I feel indecisive.',
'Q18_15': 'I am relaxed.',
'Q18_16': 'I feel content.',
'Q18_17': 'I am worried.',
'Q18_18': 'I feel confused.',
'Q18_19': 'I feel steady.',
'Q18_20': 'I feel pleasant.',
'Q19_1': 'I have disturbing thoughts.',
'Q19_2': 'I lack self-confidence.',
'Q19_3': 'I feel secure.',
'Q19_4': 'I make decisions easily.',
'Q19_5': 'I feel inadequate.',
'Q19_6': 'I am content.',
'Q19_7': 'Some unimportant thought runs through my mind and bothers me.',
'Q19_8': 'I take disappointments so keenly that I can’t put them out of my mind.',
'Q19_9': 'I am a steady person.',
'Q19_10': 'I get in a state of tension or turmoil as I think over my recent concerns and interests.',
'Q19_11': 'I feel pleasant.',
'Q19_12': 'I have disturbing thoughts.',
'Q19_13': 'I lack self-confidence.',
'Q19_14': 'I feel secure.',
'Q19_15': 'I make decisions easily.',
'Q19_16': 'I feel inadequate.',
'Q19_17': 'I am content.',
'Q19_18': 'Some unimportant thought runs through my mind and bothers me.',
'Q19_19': 'I take disappointments so keenly that I can’t put them out of my mind.',
'Q19_20': 'I am a steady person.',
'Q21' : 'TYPE 1 Straight hair: fine and fragile to coarse and thin (curl resistant)',
'Q22'	: 'TYPE 2 Wavy hair: fine and thin to coarse and frizzy',
'Q23'	: 'TYPE 3 Curly hair: loose curls to corkscrew curls',
'Q24'	: 'TYPE 4 Kinky hair: tight coils to z-angled coils',
'Q25'	: 'On a scale of 1 through 9 indicate how sleepy you are feeling',
'Q26_1': 'I try to be nice to other people. I care about their feelings.',
'Q26_2': 'I am restless, I cannot stay still for long.',
'Q26_3': 'I get a lot of headaches, stomach-aches, or sickness.',
'Q26_4': 'I usually share with others (food, games, pens, etc.).',
'Q26_5': 'I usually share with others (food, games, pens, etc.).',
'Q26_6': 'I am usually on my own. I generally play alone or keep to myself.',
'Q26_7': 'I usually do as I am told.',
'Q26_8': 'I usually do as I am told.',
'Q26_9': 'I am helpful if someone is hurt, upset, or feeling ill.',
'Q26_10': 'I am constantly fidgeting or squirming.',
'Q26_11': 'I have one good friend or more.',
'Q26_12': 'I fight a lot. I can make other people do what I want.',
'Q26_13': 'I am often unhappy, down-hearted, or tearful.',
'Q26_14': 'Other people my age generally like me.',
'Q26_15': 'I am easily distracted. I find it difficult to concentrate.',
'Q26_16': 'I am nervous in new situations. I easily lose confidence.',
'Q27': 'To what extent do you control your screen behaviours',
'Q28': 'To what extent do you feel dependent on screens in order to function effectively in day-to-day life?',
'Q29': 'Do you feel addicted to any screen based activities?',
'Q30': 'How many social media apps do you have on your smartphone?',
'Q31': 'Are the impacts of social media on your well-being mostly positive or mostly negative?',
'Q32': 'To what extent do you find social media essential for day-to-day life?',
'Q33':'‘Do you avoid any social media?'}
#--------------------------------------------------------------------------------------------------------------------------------------------#
def correct_format(pid):
    "Checks to see if a string is alphanumeric and of length 6 to 7 characters. This is because of the format used to create PIDs for the students."
    "Arguments: (pid) an uppercase string"
    "Returns: (False) if the string is NAN or doesn't meet the criteria. (True) if it does meet the criteria."
    if not (pid.isalnum() and len(pid.strip()) in [6, 7]):
        return False
    elif (pid.isalnum() and len(pid.strip()) in [6, 7]):
        return True
#--------------------------------------------------------------------------------------------------------------------------------------------#
def check_number_of_rows(qualtricsdata, qualtricsdata_correct, qualtricsdata_incorrect):
    """
    Check if no entries have been lost when filtering out PIDs.

    Arguments:
        qualtricsdata (dict): The dictionary containing the raw questionnaire data.
        qualtricsdata_correct (dict): The dictionary containing the filtered questionnaire data
            with correct entries.
        qualtricsdata_incorrect (dict): The dictionary containing the filtered questionnaire data
            with incorrect entries.

    Returns:
        bool: True if no rows have been lost, False if rows have been lost.
    """
    if len(qualtricsdata_correct)+len(qualtricsdata_incorrect)==len(qualtricsdata):
        return True

#--------------------------------------------------------------------------------------------------------------------------------------------#
def filter_qualtrics(qualtricsdata):
    """
    Checks the PIDs and filters them out. 

    Arguments:
        qualtricsdata (dict): A dictionary of dictionaries representing the entries in the questionnaire data.

    Returns:
        tuple: A tuple containing three elements:
            - qualtricsdata (dict): The original dictionary of dictionaries with NaN ParticipantID entries removed.
            - qualtricsdata_correct (dict): A dictionary of dictionaries representing the filtered questionnaire data
              with correct format PIDs.
            - qualtricsdata_incorrect (dict): A dictionary of dictionaries representing the filtered questionnaire data
              with incorrect format PIDs.
    """
    # Iterate through the qualtrics data (dictionary) and get rid of any entries with NaN ParticipantID
    qualtricsdata_noblanks = {index: data for index, data in qualtricsdata.items() if data['ParticipantID']!='NAN'}
    #Iterate through dictionary and to find entries with the incorrect format
    qualtricsdata_incorrect= {index: data for index, data in qualtricsdata.items() if not correct_format(data['ParticipantID'])}
    #Iterates through those entries to find ones which are in the correct format
    qualtricsdata_correct= {index: data for index, data in qualtricsdata_noblanks.items() if correct_format(data['ParticipantID'])}
    """Just checking that no data has been lost in filtering"""
    #Checking no rows have been lost 
    if check_number_of_rows(qualtricsdata, qualtricsdata_correct, qualtricsdata_incorrect)==True:
        return qualtricsdata, qualtricsdata_correct, qualtricsdata_incorrect
    else:
        print("Some data has been lost when filtering out the incorrect PIDs")
        return 
#--------------------------------------------------------------------------------------------------------------------------------------------#
def read_qualtrics_data(filenameQualtrics):
    """
    Reads the .csv file which contains the qualtricsdata and sets some data types and formats. This function has been designed for the July 2023
    versions of the questionnaires, please double check the column names if the survey is updated.

    Arguments:
        filenameQualtrics (str): The file path for either the CN or the Post CN questionnaire.

    Returns:
        tuple: A tuple containing three elements:
            - qualtricsdata (dict): A dictionary of dictionaries representing the entries in the questionnaire data.
            - qualtricsdata_correct (dict): A dictionary of dictionaries representing the filtered questionnaire data
              with correct PIDs.
            - qualtricsdata_incorrect (dict): A dictionary of dictionaries representing the filtered questionnaire data
              with incorrect PIDs.
    """    
    #Reading .csv to a dataframe (Skipping first row as qualtrics exports two header rows)    
    qualtricsdataframeraw = pd.read_csv(filenameQualtrics, skiprows=[1])
    
    """Doing some housekeeping stuff like changing column names, getting rid of irrelevant data and setting data types"""
    #Accounting for the fact that participant ID is asked for in different questions
    #For the CN it is Q5 and for PostCN it is Q1
    if 'Post' in filenameQualtrics:
        questionno = 'Q1'
        #getting the name in case we need to name a file later
        #name= 'PostCitizenneuroscienceQuestionnaire'
    else: 
        questionno = 'Q5'
        #getting the name in case we need to name a file later
        #name= 'CitizenneuroscienceQuestionnaire'
    #Change name of columns so the functions can just refer to Participant ID
    if questionno in ['Q1', 'Q5']:
        qualtricsdataframe = qualtricsdataframeraw.astype({questionno: 'str', 'Progress': 'int32', 'Finished': 'bool'})
        #for the Post CN questionnaire
        if questionno == 'Q1':
            #renaming the important columns
            qualtricsdataframe.rename(columns={questionno: 'ParticipantID', 
                                                  'Progress': 'PostProgress', 
                                                  'Finished' : 'PostFinished',
                                                 'Duration (in seconds)': 'PostDuration (in seconds)'}, inplace=True)
            qualtricsdataframe=qualtricsdataframe.drop(columns='Unnamed: 18')
        #for the CN questionnaire
        elif questionno == 'Q5':
            #renaming the important columns
            qualtricsdataframe.rename(columns={questionno: 'ParticipantID', 
                                                  'Progress': 'CNProgress', 
                                                  'Finished' : 'CNFinished',
                                                 'Duration (in seconds)': 'CNDuration (in seconds)'}, inplace=True)
    else:
        #stopping the whole thing if 
        print('Please check the files to see what the column for participant ID is called')
        return
    #Getting rid of some of the nonsense columns like start date and location since it tells us nothing
    pointlesscolumns=['StartDate', 'RecipientEmail' , 'RecipientFirstName', 'RecipientLastName', 'EndDate', 'Status', 
                      'IPAddress', 'ExternalReference', 'LocationLatitude', 'LocationLongitude', 
                      'DistributionChannel', 'ResponseId', 'RecordedDate', 'UserLanguage']
    qualtricsdataframe=qualtricsdataframe.drop(columns=pointlesscolumns)
    #Making all the PIDs uppercase
    qualtricsdataframe['ParticipantID'] = qualtricsdataframe['ParticipantID'].str.upper()
    #Turning the dataframe into a dictionary
    qualtricsdata=qualtricsdataframe.to_dict('index')
    #Calling filter_qualtrics to get the original data, the data for correct pids and the data for incorrect pids
    qualtricsdata, qualtricsdata_correct, qualtricsdata_incorrect=filter_qualtrics(qualtricsdata)
    return qualtricsdata, qualtricsdata_correct, qualtricsdata_incorrect
#--------------------------------------------------------------------------------------------------------------------------------------------#
def read_data_record(filenameDatarecord):
    """
    Reads the .csv file which contains the data record. Sets some data types and formats.

    Arguments:
        filenameDatarecord (str): The file path for the data record.

    Returns:
        tuple: A tuple containing two elements:
            - datarecord (dict): A dictionary of dictionaries representing the entries in the data record.
            - datarecordpids (pd.Series): A series containing the participant IDs contained in the data record.
    """
    #reads the .csv datarecord
    datarecordframe=pd.read_csv(filenameDatarecord)
    #sets the data types
    datarecordframe = datarecordframe.astype({'Participant ID': 'str'})
    #ensures all strings are uppercase
    datarecordframe['Participant ID'] = datarecordframe['Participant ID'].str.upper()
    #creating a series which contains the participant IDs contained in the data record                    
    datarecordpids=datarecordframe['Participant ID']
    #creates a dictionary of the data record so its easier to handle
    datarecord=datarecordframe.to_dict('index')
    return datarecord, datarecordpids
#--------------------------------------------------------------------------------------------------------------------------------------------#
def matches(datarecordpids, pid):
    """
    Checks if the PID from the survey data appears in the data record.
    
    Arguments:
        datarecordpids (pd.Series): A series containing the participant IDs from the data record.
        pid (str): A string representing the PID taken from the survey data.
    
    Returns:
        bool: True if the PID appears in the data record, False otherwise.
    """
    if pid in datarecordpids:
        return True
#--------------------------------------------------------------------------------------------------------------------------------------------#
def find_add_matches(datarecord, datarecordpids, qualtricsdata):
    """
    Updates the datarecord dictionary with the data from matching PIDs in the qualtricsdata.

    Arguments:
        datarecord (dict): A dictionary of the data record.
        datarecordpids (pd.Series): A Series containing the Participant IDs from the data record.
        qualtricsdata (dict): A dictionary of dictionaries representing the entries in the questionnaire data.

    Returns:
        dict: The updated datarecord dictionary with merged data.
    """
    # Iterate through each entry in qualtricsdata
    for index, data in qualtricsdata.items():
        # Extract the ParticipantID from the current entry in qualtricsdata
        participant_id = data['ParticipantID']
        
        # Check if the ParticipantID exists in datarecordpids (the Series of Participant IDs from datarecord)
        if participant_id in datarecordpids.values:
            # Find the index of the matching participant_id in datarecordpids
            matching_index = next((index for index, pid in datarecordpids.items() if pid == participant_id), None)
            # If a matching index is found, update the datarecord entry with the data from qualtricsdata
            if matching_index is not None:
                datarecord[matching_index].update(data)           
    return datarecord
#--------------------------------------------------------------------------------------------------------------------------------------------#
def participant_id_numbers(data_correct, data_incorrect):
    """
    Calculate participant ID statistics.
    
    This function takes two dictionaries, `data_correct` and `data_incorrect`, representing filtered questionnaire data
    with correct and incorrect participant IDs, respectively. It calculates the number of incorrect participant IDs,
    the number of correct participant IDs, and the percentage of incorrect participant IDs relative to the correct ones.
    
    Arguments:
        data_correct (dict): A dictionary of dictionaries representing the filtered questionnaire data with correct participant IDs.
        data_incorrect (dict): A dictionary of dictionaries representing the filtered questionnaire data with incorrect participant IDs.
    
    Returns:
        tuple: A tuple containing three elements:
            - incorrect (int): The number of incorrect participant IDs.
            - correct (int): The number of correct participant IDs.
            - percent (float): The percentage of incorrect participant IDs relative to the correct ones.
    """
    incorrect=len(data_incorrect)
    correct=len(data_correct)
    percent=(incorrect/correct)*100
    return incorrect, correct, percent
#--------------------------------------------------------------------------------------------------------------------------------------------#
def participant_id_format_info(CNdata_correct, CNdata_incorrect,POSTdata_correct, POSTdata_incorrect):
    """
   Generate participant ID format information summary.

   This function takes four sets of dictionaries, `CNdata_correct`, `CNdata_incorrect`, `POSTdata_correct`,
   and `POSTdata_incorrect`, representing filtered questionnaire data with correct and incorrect participant IDs,
   both during and after the session. It calculates the number of correct and incorrect participant IDs, as well as
   the percentage of incorrect participant IDs relative to the correct ones, for both the CN (Citizen Neuroscience)
   and POST (Post Citizen Neuroscience) datasets.

   Arguments:
       CNdata_correct (dict): A dictionary of dictionaries representing the filtered CN questionnaire data with correct participant IDs during the session.
       CNdata_incorrect (dict): A dictionary of dictionaries representing the filtered CN questionnaire data with incorrect participant IDs during the session.
       POSTdata_correct (dict): A dictionary of dictionaries representing the filtered POST questionnaire data with correct participant IDs after the session.
       POSTdata_incorrect (dict): A dictionary of dictionaries representing the filtered POST questionnaire data with incorrect participant IDs after the session.

   Returns:
       pd.DataFrame: A DataFrame summarizing the participant ID format information as follows:
                     - Rows: 'During session', 'After session'
                     - Columns: 'Number of Correctly Entered PIDs', 'Number of Incorrectly Entered PIDs', '%'
   """
    #Before
    CNincorrect, CNcorrect, CNpercent= participant_id_numbers(CNdata_correct, CNdata_incorrect)
    #After
    POSTincorrect,POSTcorrect,POSTpercent=participant_id_numbers(POSTdata_correct, POSTdata_incorrect)
    
    
    #creating a dictionary of this data
    summarydata={'Number of Correctly Entered PIDs':[CNcorrect, POSTcorrect],
                 'Number of Incorrectly Entered PIDs':[CNincorrect, POSTincorrect],
                 '%' : [CNpercent, POSTpercent]}

    summaryinfo=pd.DataFrame(data=summarydata, index=["During session", "After session"])
    return summaryinfo

#--------------------------------------------------------------------------------------------------------------------------------------------
def completion_data_summary(FINALdatarecordframe):
    
    """
    Generates a summary table of completion data based on the provided data record frame.
    
    Arguments:
        FINALdatarecordframe (pd.DataFrame): The DataFrame containing completion data and progress for different tasks.
    
    Returns:
        pd.DataFrame: A DataFrame summarizing the completion data as follows:
                     - Rows: 'RS only', 'Audio only', 'Both tasks', 'Neither Tasks'
                     - Columns: 'CN only', 'Post CN only', 'Both surveys', 'Neither survey'
    """
    completiondata= FINALdatarecordframe[['RS', 'Audio', 'CNProgress','PostProgress']]
    #Doing this based on the table in google sheets sorry
    #RS and CN
    a= len( completiondata.loc[(completiondata['RS'] == 'Y')&(pd.isna(completiondata['Audio'])==True) & (completiondata['CNProgress'] ==100 )& (pd.isna(completiondata['PostProgress'])==True)])
    #RS AND Post
    b= len( completiondata.loc[(completiondata['RS'] == 'Y') &(pd.isna(completiondata['Audio'])==True)&(pd.isna(completiondata['CNProgress'])==True)& (completiondata['PostProgress'] ==100 )])
    #RS and both surveys
    c=len( completiondata.loc[(completiondata['RS'] == 'Y') &(pd.isna(completiondata['Audio'])==True)& (completiondata['CNProgress'] ==100 )& (completiondata['PostProgress'] ==100 )])
    #RS and neither survey
    d=len( completiondata.loc[(completiondata['RS'] == 'Y')&(pd.isna(completiondata['Audio'])==True) & (pd.isna(completiondata['CNProgress'])==True)& (pd.isna(completiondata['PostProgress'])==True)])
    RS=[a,b,c,d]
    #Audio and CN
    e= len( completiondata.loc[(pd.isna(completiondata['RS'])==True) &(completiondata['Audio'] == 'Y')& (completiondata['CNProgress'] ==100 )& (pd.isna(completiondata['PostProgress'])==True)])
    #Audio and Post 
    f= len( completiondata.loc[(pd.isna(completiondata['RS'])==True)&(completiondata['Audio'] == 'Y') &(pd.isna(completiondata['CNProgress'])==True)& (completiondata['PostProgress'] ==100 )])
    #Audio and both surveys
    g=len( completiondata.loc[(pd.isna(completiondata['RS'])==True)& (completiondata['Audio'] == 'Y') &(completiondata['CNProgress'] ==100 )& (completiondata['PostProgress'] ==100 )])
    #Audio and neither survey
    h=len( completiondata.loc[(pd.isna(completiondata['RS'])==True) &(completiondata['Audio'] == 'Y')& (pd.isna(completiondata['CNProgress'])==True)& (pd.isna(completiondata['PostProgress'])==True)])
    Audio=[e,f,g,h]
    #Both tasks and CN
    i= len( completiondata.loc[(completiondata['RS'] == 'Y') & (completiondata['Audio'] =='Y' ) & (completiondata['CNProgress'] ==100 )& (pd.isna(completiondata['PostProgress'])==True)])
    #Both tasks and Audio
    j=len( completiondata.loc[(completiondata['RS'] == 'Y') & (completiondata['Audio'] =='Y' ) &(pd.isna(completiondata['CNProgress'])==True)& (completiondata['PostProgress'] ==100 ) ])
    #Both tasks and both surveys
    k=len( completiondata.loc[(completiondata['RS'] == 'Y') & (completiondata['Audio'] =='Y' )& (completiondata['CNProgress'] ==100 )& (completiondata['PostProgress'] ==100 )])
    #Both tasks and neither survey
    h=len( completiondata.loc[(completiondata['RS'] == 'Y') & (completiondata['Audio'] =='Y' ) & (pd.isna(completiondata['CNProgress'])==True)& (pd.isna(completiondata['PostProgress'])==True)])
    RS_Audio=[i,j,k,h]
    #Neither task and CN
    m= len( completiondata.loc[(pd.isna(completiondata['RS'])==True)&(pd.isna(completiondata['Audio'])==True) & (completiondata['CNProgress'] ==100 )& (pd.isna(completiondata['PostProgress'])==True)])
    #Neither task and Post
    n= len( completiondata.loc[(pd.isna(completiondata['RS'])==True)&(pd.isna(completiondata['Audio'])==True)&(pd.isna(completiondata['CNProgress'])==True) & (completiondata['PostProgress'] ==100 )])
    #Neither task and both surveys
    o= len( completiondata.loc[(pd.isna(completiondata['RS'])==True)&(pd.isna(completiondata['Audio'])==True) & (completiondata['CNProgress'] ==100 )& (completiondata['PostProgress'] ==100 )])
    Neither_task=[m,n,o,'N/A']
    completiondata_summary=pd.DataFrame(data=[RS, Audio, RS_Audio, Neither_task],index=['RS only', 'Audio only', 'Both tasks', 'Neither Tasks'], columns=['CN only', 'Post CN only', 'Both surveys', 'Neither survey'])
    return completiondata_summary
#--------------------------------------------------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------------------------------------------#
def get_completion_data(filenameDatarecord, filenameCN, CNnames, filenamePOST, POSTnames):
    """
    Generate completion data and summary information and save to an MS Excel file.

    This function takes filenames (PLEASE CHECK THESE ARE CORRECT) and corresponding data from CitizenNeuroscience (CN) and PostCitizenNeuroscience (POST)
    questionnaires, as well as their corresponding participant ID names. It then processes the data, finds matching PIDs
    in the data record, and creates a final data record. Additionally, it renames columns, handles hair type values (PLEASE CHECK THESE ARE CORRECT), and
    calculates summary information about participant ID formats and key parts of the data record. It then creates an Excel 
    file containing all the data that has been found.

    Arguments:
        filenameDatarecord (str): The file path for the data record.
        filenameCN (str): The file path for the CN questionnaire.
        CNnames (dict): A dictionary mapping the participant ID names from CN to desired names.
        filenamePOST (str): The file path for the POST questionnaire.
        POSTnames (dict): A dictionary mapping the participant ID names from POST to desired names.

    Returns:
        file: Participant Completion Data.xlsx
        tuple: A tuple containing three elements:
            - FINALdatarecordframe (pd.DataFrame): The final data record DataFrame after processing and merging.
            - pidformat_summaryinfo (pd.DataFrame): A DataFrame summarizing participant ID format information.
            - completiondata_summaryinfo (pd.DataFrame): A DataFrame summarizing key parts of the data record.
    """
    #getting the CitizenNeuroscience Data which has been formatted and stuff 
    CNdata, CNdata_correct, CNdata_incorrect=read_qualtrics_data(filenameCN)
    #getting the PostCitizenNeuroscience Data also 
    POSTdata,POSTdata_correct, POSTdata_incorrect=read_qualtrics_data(filenamePOST)
    #getting the data record so we can find matches
    datarecord, datarecordpids = read_data_record(filenameDatarecord)
    
    #finding the matching PIDs in the first questionnaire data and combining the data record and questionnaire data
    #doing CN first but it doesn't actually matter
    CNdatarecord=find_add_matches(datarecord,datarecordpids,  CNdata)
    
    #THIS IS A REALLY STUPID AND LONG WAY OF RENAMING THE COLUMNS 
    #BECAUSE NESTED DICTIONARIES ARE ????
    #Turning data dictionary into a frame
    CNdatarecordframe=pd.DataFrame(CNdatarecord)
    #Renaming stuff based on a dictionary names 
    CNdatarecordframe.rename(index=CNnames, inplace=True)
    #turning it back into a dictionary cause im stupid 
    CNdatarecord=CNdatarecordframe.to_dict()
    
    #finding the matching PIDs in the second questionnaire data and combining the data record and questionnaire data
    #!!!!! This time, putting the data record created above so that all the data is combined !!!!!
    FINALdatarecord=find_add_matches(CNdatarecord,datarecordpids,   POSTdata)
    
    #Turning data dictionary into a frame for exporting 
    FINALdatarecordframe=pd.DataFrame(FINALdatarecord)
    #Renaming stuff based on a dictionary names 
    FINALdatarecordframe.rename(index=POSTnames, inplace=True)
    FINALdatarecordframe=FINALdatarecordframe.T
    #Changing hair type values 
    FINALdatarecordframe.replace({'IM_7NzSARqhuHLQW1M':'21_A','IM_0PATfSDiU0MucVU' :'21_B', 'IM_czKhNU5pe94Y0kK':'21_C', 
                                       'IM_enwG4tt3amNzFXw':'22_A','IM_eySJ0htWgQY5DaC':'22_B','IM_0vSelxTIopiVWtw':'22_C',
                                       'IM_bswZCSptk8hxLcq':'23_A','IM_290IyvtNJJa9Vsy':'23_B', 
                                       'IM_6LONnoY4KGNXuCy': '24_A','IM_7PTiMnlDQ3VjnAq': '24_B' }, inplace=True)
    #Calling participant_id_format_info to get table summarising how many students struggled with correctly entering their pid
    pidformat_summaryinfo= participant_id_format_info(CNdata_correct, CNdata_incorrect,POSTdata_correct, POSTdata_incorrect)
    #Calling completion_data_summary to get table summarising key parts of the data record
    completiondata_summaryinfo=completion_data_summary(FINALdatarecordframe)
    #Writing that data record to an excel file
    with pd.ExcelWriter('C:/Users/layla/Documents/Psychology stuff/Particpant Completion/Participant Completion Data.xlsx') as writer:
        FINALdatarecordframe.to_excel(writer, sheet_name='Data Record')
        pidformat_summaryinfo.to_excel(writer, sheet_name='PID format data')
        completiondata_summaryinfo.to_excel(writer, sheet_name='Completion Numbers')
    return FINALdatarecordframe, pidformat_summaryinfo, completiondata_summaryinfo

#--------------------------------------------------------------------------------------------------------------------------------------------
"""PLEASE CHANGE THE FILE LOCATIONS. The dictionary at the beginning specifies which question each number corresponds to."""


filenameDatarecord = 'C:/Users/layla/Documents/Psychology stuff/Particpant Completion/Data Record Sorted Out.csv'
filenameCN = 'C:/Users/layla/Documents/Psychology stuff/Particpant Completion/CN Questionnaire Results.csv'
filenamePOST = 'C:/Users/layla/Documents/Psychology stuff/Particpant Completion/Post CN Questionnaire Results.csv'

FINALdatarecordframe,pidformat_summaryinfo,completiondata_summaryinfo =get_completion_data(filenameDatarecord, filenameCN, CNnames, filenamePOST, POSTnames)


#--------------------------------------------------------------------------------------------------------------------------------------------
end = time.time()

#Subtract Start Time from The End Time
total_time = end - start
print("\n"+ str(total_time) + " seconds")




