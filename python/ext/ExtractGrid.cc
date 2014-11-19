#include <iomanip>
#include <iostream>
#include "Document.h"
#include "NaiveEGrid.h"

void printGrid(const string& d, symToIntToInt& roles, int len);

int main(int argc, char* argv[])
{
    appInit(DATA_PATH);

    EGridModel* mod = NULL;
    mod = new NaiveEGrid(0, 0, 0, 0);

    std::string name = "std::cin";
    Document* doc = new Document(std::cin, name);

    if(!doc->empty())
    {
        mod->initCaches(*doc);
        printGrid("std::cin", mod->roles(), doc->size());
        mod->clearCaches();
    }
}

void printGrid(const string& d, symToIntToInt& roles, int len)
{
    symSet printed;

    for(int i=0; i < len; i++)
    {
        for(symToIntToInt::iterator entity = roles.begin();
            entity != roles.end();
            entity++)
        {
            if(roles[entity->first][i] != T_NONE && 
               !contains(printed, entity->first))
            {

                cout<<setw(20)<<uc(SYMTAB->toString(entity->first));

                for(intToInt::iterator sym = entity->second.begin();
                    sym != entity->second.end();
                    sym++)
                {
                    if(sym->first > 28)
                    {
                        break;
                    }

                    cout<<" "<<NP::roleToString(sym->second);
                }
                cout<<"\n";

                printed.insert(entity->first);
            }
        }
    }
}
