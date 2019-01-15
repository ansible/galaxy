import * as React from 'react';
import { Injector } from '@angular/core';

interface ContextDef {
    injector: Injector;
}

export const InjectorContext = React.createContext({} as ContextDef);
