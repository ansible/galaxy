import { Component, Input, OnInit } from '@angular/core';

import { CardConfig } from 'patternfly-ng/card/basic-card/card-config';

import * as moment from 'moment';

@Component({
    selector: 'card-versions',
    templateUrl: './versions.component.html',
    styleUrls: ['./versions.component.less'],
})
export class CardVersionsComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'CardVersionsComponent';

    constructor() {}

    _versions: any[] = [];

    @Input()
    set versions(data: any[]) {
        if (data) {
            data.forEach(version => {
                this._versions.push({
                    date: moment(
                        version['commit_date'] || version['created'],
                    ).fromNow(),
                    tag: version['tag'] || version['version'],
                });
            });
        }
    }

    get versions(): any[] {
        return this._versions;
    }

    config: CardConfig;

    ngOnInit() {
        this.config = {
            titleBorder: true,
            topBorder: true,
        } as CardConfig;
    }
}
