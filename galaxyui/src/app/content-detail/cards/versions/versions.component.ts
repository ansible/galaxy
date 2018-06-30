import {
    Component,
    Input,
    OnInit
} from '@angular/core';

import { CardConfig }     from 'patternfly-ng/card/basic-card/card-config';
import { Content }        from '../../../resources/content/content';
import { Repository }     from '../../../resources/repositories/repository';

import * as moment        from 'moment';

@Component({
    selector: 'card-versions',
    templateUrl: './versions.component.html',
    styleUrls: ['./versions.component.less']
})
export class CardVersionsComponent implements OnInit {

    constructor() {}

    _versions: any[];

    @Input()
    set versions(data: any[]) {
        this._versions = data;
        if (data) {
            data.forEach(version => {
                version['date'] = moment(version['commit_date']).fromNow();
            });
        }
    }

    get versions(): any[] { return this._versions; }

    config: CardConfig;

    ngOnInit() {
        this.config = {
            titleBorder: true,
            topBorder: true
        } as CardConfig;
    }
}
