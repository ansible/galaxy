import {
    Component,
    Input,
    OnInit
} from '@angular/core';

import { CardConfig }     from 'patternfly-ng/card/basic-card/card-config';

@Component({
    selector: 'card-cloud-platforms',
    templateUrl: './cloud-platforms.component.html',
    styleUrls: ['./cloud-platforms.component.less']
})
export class CardCloudPlatformsComponent implements OnInit {

    constructor() {}

    @Input() cloudPlatforms: any[];

    config: CardConfig;

    ngOnInit() {
        this.config = {
            titleBorder: true,
            topBorder: true
        } as CardConfig;
    }
}
