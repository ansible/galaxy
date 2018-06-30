import {
    Component,
    Input,
    OnInit
} from '@angular/core';

import { CardConfig }     from 'patternfly-ng/card/basic-card/card-config';
import { Content }        from '../../../resources/content/content';
import { Repository }     from '../../../resources/repositories/repository';
import { Platform }       from '../../../resources/platforms/platform';

@Component({
    selector: 'card-platforms',
    templateUrl: './platforms.component.html',
    styleUrls: ['./platforms.component.less']
})
export class CardPlatformsComponent implements OnInit {

    constructor() {}

    @Input() platforms: Platform[];

    config: CardConfig;

    ngOnInit() {
        this.config = {
            titleBorder: true,
            topBorder: true
        } as CardConfig;
    }
}
