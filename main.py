#Importação das bibliotecas usadas

from distutils.dep_util import newer_group
from sklearn.feature_extraction.text import CountVectorizer
from itertools import count
import PyPDF2
import re
import numpy as np
import mysql.connector
from mysql.connector import Error

###exemplo de comentário
#conexão com o banco
try:
  con = mysql.connector.connect(host = 'localhost', database = 'pji', user = 'root', password = 'rhm0712')
  if(con.is_connected):
    cursor = con.cursor()
    cursor.execute("select database();")
    linha = cursor.fetchone()
    print("Conectado ao banco", linha)
    
except Error as erro:
  print("Falha ao conectar ao banco: {}".format(erro))
      
#Calculo similaridade

def similaridade (texto_comparar, base, n ):
   
    counts = CountVectorizer(analyzer='word', ngram_range=(n,n))
    n_grams = counts.fit_transform([texto_comparar,base])
    vocab2int = counts.fit([texto_comparar,base]).vocabulary_
    n_grams_array = n_grams.toarray()
    intersection_list = np.amin(n_grams.toarray(), axis=0)
    intersection_count = np.sum(intersection_list)
    index_A = 0
    A_count = np.sum(n_grams.toarray()[index_A])
    return (intersection_count/A_count)
   
#Abertura PDF
 
pdf_file = open('Cadernos/CadernoDeResumos2011.pdf', 'rb')
 
#Conversão para binario

dados_pdf_feira1 = PyPDF2.PdfFileReader(pdf_file)

#Declaração das variaveis que vão ser usadas

quantidadePT = 37 + 41 
quantidadeP = 41
quantidadeV = quantidadeP - 1
projetos = []
matrizV = []
pQuebrados = []
pTitulo = []
pAutores = []
pOrientadores = []
pCoOrientadores = []
pResumos = []
pTratados = []
 
#Extração dos dados do PDF

for i in range(quantidadeP):
    pagina = dados_pdf_feira1.getPage(i+8)
    projeto = pagina.extractText()
    projetos.append(re.sub('\n', ' ', projeto))

#Quebra do Conteudo em palavras

for i in range(quantidadeP):
    tempo = projetos[i]
    banana = str(tempo)
    for j in banana.split():
        pQuebrados.append(j)
        
#corrige sintaxes
        
for i in range(len(pQuebrados)):
  if(pQuebrados[i] == "d'água,"):
    pQuebrados[i] = "de agua,"
    
#Identifica onde palavras iguais a Resumo

localResumo = []
for i in range(len(pQuebrados)):
    if pQuebrados[i] == "Resumo":
        localResumo.append(i)
        pQuebrados [i] = ""

#Identifica onde palavras iguais a Autores

localAutores = []
for i in range(len(pQuebrados)):
    if pQuebrados[i] == "Autores:":
      localAutores.append(i)
      pQuebrados [i] = ""

#Identifica onde palavras iguais a Titulo

localTitulo = []
for i in range(len(pQuebrados)):
    if pQuebrados[i] == "Título:":
      localTitulo.append(i)
      pQuebrados [i] = ""

#Identifica onde palavras iguais a Orientador

localOrientador = []
for i in range(len(pQuebrados)):
    if pQuebrados[i] == "Orientador: " or pQuebrados[i] == "Orientador:" or pQuebrados[i] == " Orientador:":
      localOrientador.append(i)
      pQuebrados [i] = ""

#Identifica onde palavras iguais a Co-Orientador

localCoOrientador = []
for i in range(len(pQuebrados)):
    if pQuebrados[i] == "Co-orientador:":
      localCoOrientador.append(i)
      pQuebrados [i] = ""

#Une as informações presentes no titulo

for i in range(len(localTitulo)):
  tit = ""
  p1 = localTitulo[i]
  p2 = localAutores[i]
  for j in range(p1,p2):
    if(pQuebrados[j] != "Título:" and pQuebrados[j] != "Autores:"):
      tit += (pQuebrados[j] + " ")
      pQuebrados[j] = ""
  pTitulo.append(tit)

#Une as informações presentes no Autores

for i in range(len(localAutores)):
  aut = ""
  p1 = localAutores[i]
  p2 = localOrientador[i]
  for j in range(p1,p2):
    if(pQuebrados[j] != "Autores:" and pQuebrados[j] != "Orientador"):
      aut += (pQuebrados[j] + " ")
      pQuebrados [j] = ""
  pAutores.append(aut)


#Une as informações presentes no Orientador

for i in range(len(localOrientador)):
  ori = ""
  p1 = localOrientador [i]
  p2 = localCoOrientador [i]
  for j in range(p1,p2):
    if(pQuebrados[j] != "Orientador:" and pQuebrados[j] != "Co-orientador:"):
      ori += (pQuebrados[j] + " ")
      pQuebrados [j] = ""
  pOrientadores.append(ori)

#Une as informações presentes no Co-Orientador

for i in range(len(localCoOrientador)):
  coo = ""
  p1 = localCoOrientador [i]
  p2 = localResumo [i]
  for j in range(p1,p2):
    if(pQuebrados[j] != "Co-orientador:" and pQuebrados[j] != "Resumo"):
      coo += (pQuebrados[j] + " ")
      pQuebrados [j] = ""
  pCoOrientadores.append(coo)

#Une as informações presentes no Resumo

for i in range(len(localTitulo)-1):
  proj = ""
  p1 = localResumo[i]
  p2 = localTitulo[i+1]
  for j in range(p1,p2):
    if(pQuebrados[j] != "Resumo" and pQuebrados[j] != "Título:"):
      proj += (pQuebrados [j] + " ")
      pQuebrados [j] = ""
  pResumos.append(proj)


#Coleta o ultimo resumo restante

projF = ""
for j in range(len(pQuebrados)):
  if(pQuebrados[j] != ""):
    projF += (pQuebrados[j] + " ")
    pQuebrados [j] = ""
pResumos.append(projF)

#Une Titulo e Projeto para a compração

resumo = ""
for i in range(len(pTitulo)):
  resumo += (pTitulo [i] + pResumos [i])
  pTratados.append(resumo)
  resumo = ""

#Inicio feira 2

#Abertura PDF
 
pdf_file2 = open('Cadernos/Caderno de Resumos 2012.pdf', 'rb')
 
#Conversão para binario

dados_pdf_feira2 = PyPDF2.PdfFileReader(pdf_file2)

#Declaração das variaveis que vão ser usadas


quantidadeP = 37
quantidadeV = quantidadePT - 1
projetos = []
matrizV = []
pQuebrados = []
maisSimilar = [0] * quantidadePT
 
#Extração dos dados do PDF

for i in range(quantidadeP):
    pagina = dados_pdf_feira2.getPage(i+8)
    projeto = pagina.extractText()
    projetos.append(re.sub('\n', '', projeto))
    
    
#Quebra do Conteudo em palavras

for i in range(quantidadeP):
    tempo = projetos[i]
    banana = str(tempo)
    for j in banana.split():
        pQuebrados.append(j)

with open('AB.txt', 'w') as arquivo:
  for q in range(len(pQuebrados)):
    print(q+1, pQuebrados[q], file=arquivo)
   
#Remove palavras que não participam da formatação correta
    
for i in range(len(pQuebrados)):
      if(pQuebrados[i] == ":" or pQuebrados[i] == " " or pQuebrados[i] == "tores" or pQuebrados[i] == "r:" or pQuebrados[i] == "o:" or pQuebrados[i] == "lo:"):
            pQuebrados[i] = ""
  

#Identifica onde palavras iguais a Resumo

localResumo = []
for i in range(len(pQuebrados)):
    if pQuebrados[i] == "Resumo:":
        pQuebrados[i] = ""  
        localResumo.append(i)

#Identifica onde palavras iguais a Autores

localAutores = []
for i in range(len(pQuebrados)):
    if pQuebrados[i] == "Autores" or pQuebrados[i] == "Autores:" or pQuebrados[i] == "Au" :
      pQuebrados[i] = ""
      localAutores.append(i)

#Identifica onde palavras iguais a Titulo

localTitulo = []
for i in range(len(pQuebrados)):
    if pQuebrados[i] == "Título" or pQuebrados[i] == "Título:" or pQuebrados[i] == "Títul" or pQuebrados[i] == "Títu":
      pQuebrados[i] = ""
      localTitulo.append(i)

#Identifica onde palavras iguais a Orientador

localOrientador = []
for i in range(len(pQuebrados)):
    if pQuebrados[i] == "Orientador:" :
      pQuebrados[i] = ""
      localOrientador.append(i)

#Identifica onde palavras iguais a Co-Orientador

localCoOrientador = []
for i in range(len(pQuebrados)):
    if pQuebrados[i] == "-orientador:" or pQuebrados[i] == "Co-orientador:" or pQuebrados[i] == "-orientado" or pQuebrados[i] == "-orientador" :
      pQuebrados[i] = ""
      localCoOrientador.append(i)


#Une as informações presentes no titulo

for i in range(len(localTitulo)):
  tit = ""
  p1 = localTitulo[i]
  p2 = localAutores[i]
  for j in range(p1,p2):
    if(pQuebrados[j] != "Título:" and pQuebrados[j] != "Autores:"):
      tit += (pQuebrados[j] + " ")
      pQuebrados[j] = ""
  pTitulo.append(tit)

#Une as informações presentes no Autores

for i in range(len(localAutores)):
  aut = ""
  p1 = localAutores[i]
  p2 = localOrientador[i]
  for j in range(p1,p2):
    if(pQuebrados[j] != "Autores:" and pQuebrados[j] != "Orientador"):
      aut += (pQuebrados[j] + " ")
      pQuebrados [j] = ""
  pAutores.append(aut)


#Une as informações presentes no Orientador

for i in range(len(localOrientador)):
  ori = ""
  p1 = localOrientador [i]
  p2 = localCoOrientador [i]
  for j in range(p1,p2):
    if(pQuebrados[j] != "Orientador:" and pQuebrados[j] != "Co-orientador:"):
      ori += (pQuebrados[j] + " ")
      pQuebrados [j] = ""
  pOrientadores.append(ori)

#Une as informações presentes no Co-Orientador

for i in range(len(localCoOrientador)):
  coo = ""
  p1 = localCoOrientador [i]
  p2 = localResumo [i]
  for j in range(p1,p2):
    if(pQuebrados[j] != "Co-orientador:" and pQuebrados[j] != "Resumo"):
      coo += (pQuebrados[j] + " ")
      pQuebrados [j] = ""
  pCoOrientadores.append(coo)

#Une as informações presentes no Resumo

for i in range(len(localTitulo)-1):
  proj = ""
  p1 = localResumo[i]
  p2 = localTitulo[i+1]
  for j in range(p1,p2):
    if(pQuebrados[j] != "Resumo" and pQuebrados[j] != "Título:"):
      proj += (pQuebrados [j] + " ")
      pQuebrados [j] = ""
  pResumos.append(proj)
  

#Coleta o ultimo resumo restante

projF = ""
for j in range(len(pQuebrados)):
  if(pQuebrados[j] != ""):
    projF += (pQuebrados[j] + " ")
    pQuebrados [j] = ""
pResumos.append(projF)
 
#Une Titulo e Projeto para a compração

for i in range(40,77):
  resumo = ""
  resumo += (pTitulo [i] + pResumos [i])
  pTratados.append(resumo)

#Envia os dados para serem comparados

similaridades = []
for j in range(len(pTratados)):
  base = pTratados[j]
  for k in range(len(pTratados)):
    compara = pTratados[k]
    similaridades.append(similaridade(compara, base, 1))

#Salva em uma matriz os valores
linha = []
for r in range(len(similaridades)):
  linha.append(similaridades[r])
  if (r == quantidadeV) or ((r-quantidadeV) % quantidadePT == 0):
    matrizV.append(linha)
    linha = []
 
#Define o mais similar

for r in range(len(matrizV)):
  escolhido = 0
  pontuação = 0
  for g in range(len(matrizV)):
    if(matrizV[r][g] > pontuação and matrizV[r][g] != 1):
      pontuação = matrizV[r][g]
      escolhido = g
  maisSimilar[r] = escolhido

#Cria um txt com os titulos

with open('tit.txt', 'w') as arquivo:
  for q in range(len(pTitulo)):
    print(q+1, pTitulo[q], file=arquivo)

#Cria um txt com os Autores

with open('aut.txt', 'w') as arquivo:
  for q in range(len(pAutores)):
    print(q+1, pAutores[q], file=arquivo)

#Cria um txt com os Orientador

with open('ori.txt', 'w') as arquivo:
  for q in range(len(pOrientadores)):
    print(q+1, pOrientadores[q], file=arquivo)

#Cria um txt com os Co-Orientador

with open('coo.txt', 'w') as arquivo:
  for q in range(len(pCoOrientadores)):
    print(q+1, pCoOrientadores[q], file=arquivo)

#Cria um txt com os Resumos

with open('res.txt', 'w') as arquivo:
  for q in range(len(pResumos)):
    print(q+1, pResumos[q], file=arquivo)

#Cria um txt com os Resumos do jeito quer foram analisados

with open('proj.txt', 'w') as arquivo:
  for q in range(len(pTratados)):
    print(q+1, pTratados[q], file=arquivo)

#Cria um txt com os valores de similaridade em valor de matriz
       
with open('valores.txt', 'w') as arquivo:
  linha = len(matrizV) 
  coluna = len(matrizV[0])
  for r in range (linha):
    for p in range (coluna):
      print(matrizV[r][p], file=arquivo)
  
  
#Cria um txt com os indices dos mais similares

with open('fim.txt', 'w') as arquivo:
    for q in range(len(maisSimilar)):
        print(q+1, maisSimilar[q]+1, file=arquivo)

#inserção de dados na tabela

try:
  
  for r in range(len(pAutores)):
    if(r <= 41):
      ano = "2011"
    else:
      ano = "2012"
    inserirProjetos = ("INSERT INTO projeto(pro_id, pro_nome,pro_resumo,pro_ano,pro_autores,pro_orientador,pro_coOrientador) VALUES('"+str(r)+"','"+pTitulo[r]+"','"+pResumos[r]+"','"+ano+"','"+pAutores[r]+"','"+pOrientadores[r]+"','"+pCoOrientadores[r]+"')")
    cursor.execute(inserirProjetos)
    con.commit()
    print(cursor.rowcount, "Registros inseridos na tabela!")
    
except Error as erro:
  print("Falha ao inserir dados no banco: {}".format(erro))



if(con.is_connected):
      cursor.close()
      con.close()
      print("Fim da conexão")