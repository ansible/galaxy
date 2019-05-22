import { Component, Input, OnInit } from '@angular/core';

import { CardConfig } from 'patternfly-ng/card/basic-card/card-config';
import { ContentFormat } from '../../../enums/format';

@Component({
    selector: 'card-dependencies',
    templateUrl: './dependencies.component.html',
    styleUrls: ['./dependencies.component.less'],
})
export class CardDependenciesComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'CardDependenciesComponent';

    constructor() {}

    private _dependencies: any;

    @Input()
    set dependencies(deps: any) {
        this._dependencies = [];

        if (deps) {
            if (deps.constructor === Object) {
                // Handle dependencies for collections
                const keys = Object.keys(deps);

                for (const key of keys) {
                    this._dependencies.push({
                        name: key,
                        url: '/' + key.replace('.', '/'),
                        version: deps[key],
                    });
                }
            } else {
                // Handle dependencies for repos
                deps.forEach(d => {
                    this._dependencies.push({
                        name: `${d.namespace}.${d.name}`,
                        url: `/${d.namespace}/${d.name}`,
                    });
                });
            }
        }
    }
    get dependencies(): any {
        return this._dependencies;
    }

    config: CardConfig;

    ngOnInit() {
        this.config = {
            titleBorder: true,
            topBorder: true,
        } as CardConfig;
    }
}
