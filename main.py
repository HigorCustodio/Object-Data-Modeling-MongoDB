import motor.motor_asyncio
from beanie import Document
from pydantic import Field
import beanie
import asyncio
from pprint import pprint
from bson import ObjectId

'''
   beanie.Document:
        É a classe de documento que ajuda nosso ODM a definir a as regras/Schemas aplicados ao documento criado.
    
    O que é o documento:
        É cada conjunto de dados dentro da collection do banco de dados noSQL orientado a documentos.
    
    Modelando a estrutura do banco de dados:
        class Task:
            id :int
            content :text
            is_complete :bool -> False
        
        •   Definindo um Documento:
            A maneira de definir um documento usando o beanie é semelhante a forma de 
            criação de um schema do Pydantic.

            ◘   Irá herdar a classe beanie.Document:
                class Task(beanie.Document):
                    pass
               
            ◘   O conteúdo da classe deverá conter o mesmo schema do banco de dados.
                ex:
                    class Task(beanie.Document):
                        id:int,
                        content:str
            
            ◘   Como criar validações do conteúdo do parâmetros do Schema/Documento:
                - É possível criar uma zona de validação para o conteúdo dos parâmetros 
                do Schema, desta forma é implicada uma segurança de que sempre deverá 
                seguir o padrão especifícado, caso contrário será lançado uma exceção.
                
                - Documentação Field:
                    https://docs.pydantic.dev/2.4/concepts/fields/
                
                - Para criar essa zona de validação é usado uma função da biblioteca
                Pydantic chamada Field, onde dentro da mesma, existem diversos parâmetros 
                que podem ser aplicados para restringir cada vez mais o tipo de dado e as 
                caracteristicas que serão aplicadas a ele.
                
                - Exemplos de validações:
                    Default: 
                        default(any): Receberá valor que o parâmetro apresentará como 
                        padrão.
                     
                    Restrições Numéricas:
                        Existem alguns argumentos de palavras-chave que podem ser usados 
                        para restringir valores numéricos;
                        
                        gt- Maior que
                        lt- menor que
                        ge- Maior que ou igual a
                        le- menor que ou igual a
                        multiple_of- um múltiplo do número fornecido
                        allow_inf_nan- permitir valores 'inf', '-inf','nan'
                        
                    Restrições de string¶
                        Existem campos que podem ser usados para restringir strings:
                        
                        min_length: Comprimento mínimo da string.
                        max_length: Comprimento máximo da string.
                        pattern: uma expressão regular à qual a string deve corresponder.
                        
                    Restrições decimais¶
                        Existem campos que podem ser usados para restringir decimais:
                        
                        max_digits: Número máximo de dígitos dentro do arquivo Decimal. 
                        Não inclui um zero antes da vírgula decimal ou zeros decimais à 
                        direita.
                        
                        decimal_places: Número máximo de casas decimais permitidas. Não 
                        inclui zeros decimais à direita.
                Ex:
                    from pydantic import Field
                    
                    class Task(beanie.Document):
                        id:int = Field(gt=0)
                        content:str = Field(max_length=200)

            
''' 
class Task(Document):
    id:int = Field(gt=0)
    content:str = Field(max_length=200)
    is_complete:bool = Field(default=False)
    
    def to_json(self):
        return{
            "id":self.id,
            "revision_id":self.revision_id,
            "content":self.content,
            "is_complete":self.is_complete,
        }

class ManipularBancoDados:
    def __init__(self) -> None:
        self._loop = asyncio.get_event_loop()
    
    #! CONECT:
    async def _conectar_banco_dados(self):
        '''
        Criando cliente de conexão async através do uso da biblioteca "motor".
        Sempre que é usado métodos ou funções assincronas é necessário criar uma corrotina.
        
        Sintaxe:
            client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")

        Deste modo dependemos da função motor_asyncio para criar a conexão com o banco de 
        dados usando a porta padrão do mongo localhost:27017, criando assim nosso cliente.
        
        "mongodb://localhost:27017" -> Fluxo de Conexão com o Banco de Dados.
        mongo://localhost -> Indica máquina onde está localizado o banco de dados.
        27017 -> Porta de conexão.
        
        '''
        #Linha necessária para estabelecer conexão com o banco de dados:
        client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
        
        #Usar classe beanie para inicializar o banco de dados:
        await beanie.init_beanie(database=client.beanie_teste, document_models=[Task])
    
    #! CREATE:
    @beanie.before_event(beanie.Insert)
    async def _criar_tarefas_banco(self):
        
        #! Com parâmetro id, para busca com find e find_all.
        task1 = Task(id=1, content='Content 01', is_complete=False)
        task2 = Task(id=2, content='Content 02', is_complete=True)
        task3 = Task(id=3, content='Content 03', is_complete=False)
        
        #! Sem parâmetro id, automaticamente atribui um object id aleatorio, realizar busca através do find_one.
        # task1 = Task(content='Content 01', is_complete=False) 
        # task2 = Task(content='Content 02', is_complete=True) 
        # task3 = Task(content='Content 03', is_complete=False) 
        
        lista_tarefas = [task1, task2, task3]
        for tarefa in lista_tarefas: await tarefa.insert()
    
    #! READ:
    async def _get_todas_as_tarefas(self) -> list:
        # return await Task.find_all().to_list()
        return await Task.find_all().to_list()
    
    async def _get_tarefas_por_filtro(self, filtro):
        return await Task.find(filtro).to_list()
    
    async def _get_todas_tarefas(self):
        #? Como executar um loop que retorne um json:
        print(
            '\n===================\n'
            '===Todas Tarefas===\n'
            '==================='
        )
        
        lista_tarefas = await self._get_todas_as_tarefas()
        lista_ = [tarefa.to_json() for tarefa in lista_tarefas ]
        return lista_

    async def _get_tarefas_filtro_beanie(self):
        print(
            '\n===================\n'
            'Tarefas incompletas\n'
            '==================='
        )
        lista_tarefas_incompletas = await self._get_tarefas_por_filtro(
            filtro = Task.is_complete == False
        )
        for tarefa in lista_tarefas_incompletas: pprint(tarefa.to_json())
    
    async def _get_tarefas_filtro_pydantic(self):
        print(
            '\n===================\n'
            '=Tarefas completas=\n'
            '==================='
        )
        lista_tarefas_completas = await self._get_tarefas_por_filtro(
            filtro = {"is_complete":True} 
        )
        for tarefa in lista_tarefas_completas: pprint(tarefa.to_json())

    async def _get_tarefa_id_mongodb(self, id_:str):
        '''
        Caso o documento no mongo tenha um ObjectID gerado automaticamente pelo mongo, vai ser necessário realizar a consulta deste documento através do find_one, caso o id seja setado poderá ser usado o find e o find_all para buscar os documentos.
        
        Observação: É possível realizar o uso do find_one em tarefas realizar e o find e find_all no tarefas realizando.
        '''
        # return await Task.find_one(
        #     Task.id == ObjectId("65514f10c3ab3e2b2e85f017")
        # )
        return await Task.find_one({"_id" : ObjectId(f"{id_}")})
    
    #! UPDATE:
    @beanie.after_event(beanie.Replace)
    async def _atualizar_documento_beanie_através_atributo(self, id_:str):
        '''
        Existem 2 maneiras de atualizar documentos beanie, a primeira consiste em 
        atualizar um atributo especifico, já a segunda consiste em alterar o documento 
        inteiro
        '''
        #*Primeira maneira: - Atualizando atributo específico!
        #Capturar documento:
        task = await Task.find_one({"_id" : ObjectId(id_)})
        #Atribuir novo valor:
        task.content = 'Conteúdo atualizado'
        #Salvar novo valor no banco de dados:
        await task.save()
    
    @beanie.after_event(beanie.Replace)
    async def _atualizar_documento_beanie_completo(self, id_:str):
        '''
        Existem 2 maneiras de atualizar documentos beanie, a primeira consiste em 
        atualizar um atributo especifico, já a segunda consiste em alterar o documento 
        inteiro
        '''
        #*Segunda maneira: - Atualizando documento completo!
        
        id_ = f"{id_}"
        #Capturar documento:
        task = await Task.find_one({"_id" : ObjectId(f"{id_}")})
        
        #Atribuir novo valor:
        task.content = 'Conteúdo atualizado documento completo'
        
        #Salvar novo valor no banco de dados e setando tratativa de erro:
        try:
            await task.replace()
        except (ValueError, beanie.exceptions.DocumentNotFound):
            print(f"Document With Id == {id_} Not Found!")
    
    #! DELETE:
    @beanie.after_event(beanie.Delete)
    async def _deletar_documento_específico(self):
        '''
        Deletar documento através do ObjectID
        '''        
        id_ = "65514f10c3ab3e2b2e85f018"
        
        #Capturar documento:
        task = await Task.find_one({"_id" : ObjectId(f"{id_}")})
        
        #Deletar documento:
        await task.delete()
    
    @beanie.after_event(beanie.Delete)
    async def _deletar_colection(self):
        '''
        Deletar toda a collection
        '''
        await Task.delete_all()   
    
    async def execute(self):
        await self._conectar_banco_dados()
        
        # await self._criar_tarefas_banco()
        
        tarefa = await self._get_todas_tarefas()
        pprint(tarefa)
        
        # tarefa = await self._get_tarefa_id_mongodb(id_="6551f03b093bf279ee7811dc")
       
        # await self._atualizar_documento_beanie_através_atributo(
        #     id_="6551ef9f9c3ac81e146cf45b"
        # )
        
        # await self._atualizar_documento_beanie_completo(
        #     id_="6551ef9f9c3ac81e146cf45c"
        # )
        
        # await self._deletar_colection()
    
    
    
if __name__ == '__main__':
    banco_dados = ManipularBancoDados()
    asyncio.run(banco_dados.execute())
    # asyncio.run(banco_dados._criar_tarefas_banco())
