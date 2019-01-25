import * as React from 'react';
import { Injector } from '@angular/core';

interface IContextDef {
    injector: Injector;
}

export const InjectorContext = React.createContext({} as IContextDef);
