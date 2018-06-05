import {
    Component,
    Input,
    OnInit
} from '@angular/core';

import { CardConfig }     from 'patternfly-ng/card/basic-card/card-config';
import { Content }        from '../../../resources/content/content';
import { Repository }     from '../../../resources/repositories/repository';


@Component({
    selector: 'card-dependencies',
    templateUrl: './dependencies.component.html',
    styleUrls: ['./dependencies.component.less']
})
export class CardDependenciesComponent implements OnInit {

    constructor() {}

    private _dependencies: any[];

    @Input()
    set dependencies(deps: any[]) {
        this._dependencies = []
        if (deps) {
            deps.forEach(d => {
                this._dependencies.push({
                    name: `${d.namespace}.${d.name}`,
                    url: `/${d.namespace}/${d.name}`
                })
            });
        }
    }

    get dependencies(): any[] {
        return this._dependencies;
    }

    config: CardConfig;

    ngOnInit() {
        this.config = {
            titleBorder: true,
            topBorder: true
        } as CardConfig
    }
}
