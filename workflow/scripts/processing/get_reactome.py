import pandas as pd

def protein_to_pathway():
    #protein to pathway
    url="https://reactome.org/download/current/UniProt2Reactome_All_Levels.txt"
    df=pd.read_csv(url,sep='\t')
    df.columns=[
        'source_id',
        'reactome_id',
        'url',
        'event',
        'evidence_code',
        'species'
    ]
    df = df[df['species']=='Homo sapiens']
    print(df.head())
    df.to_csv('UniProt2Reactome_All_Levels_human.csv',index=False)

def pathway_to_pmid():
    #pathway to pmid
    url="https://reactome.org/download/current/ReactionPMIDS.txt"
    df=pd.read_csv(url,sep='\t')
    df.columns=[
        'reactome_id',
        'pmid'
    ]
    print(df.head())
    df.to_csv('ReactionPMIDS.csv',index=False)

def id_to_reaction():
    #identifier to reaction
    url="https://reactome.org/download/current/UniProt2ReactomeReactions.txt"
    df=pd.read_csv(url,sep='\t')
    df.columns=[
        'source_id',
        'reactome_id',
        'url',
        'event',
        'evidence_code',
        'species'
    ]
    df = df[df['species']=='Homo sapiens']
    print(df.head())
    df.to_csv('UniProt2ReactomeReactions.csv',index=False)

def pathways():
    #pathways
    #complete list
    url="https://reactome.org/download/current/ReactomePathways.txt"
    df1=pd.read_csv(url,sep='\t')
    df1.columns=[
        'reactome_id',
        'name',
        'species'
    ]
    df1 = df1[df1['species']=='Homo sapiens']
    print(df1.head())
    df1.to_csv('ReactomePathways_human.csv',index=False)

    #hierarchy
    url="https://reactome.org/download/current/ReactomePathwaysRelation.txt"
    df2=pd.read_csv(url,sep='\t')
    df2.columns=[
        'parent',
        'child',
    ]
    print(df2.head())
    print(df2.shape)
    df2=df2[df2['parent'].isin(df1['reactome_id'])]
    print(df2.shape)
    df2.to_csv('ReactomePathwaysRelation_human.csv',index=False)


    #complex to pathway
    #url="https://reactome.org/download/current/Complex_2_Pathway_human.txt"

def get_data():
    #protein_to_pathway()
    pathways()
    #pathway_to_pmid()
    #id_to_reaction()

get_data()