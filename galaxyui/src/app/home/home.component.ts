import {
	Component,
    OnInit
}          from '@angular/core';

import {
	CardConfig
} from 'patternfly-ng/card/basic-card/card-config';

@Component({
    selector:    'home',
    templateUrl: './home.component.html',
    styleUrls:   ['./home.component.less']
})
export class HomeComponent implements OnInit {

	downloadConfig: CardConfig;
	headerTitle: string = "Home";

    constructor() {}
    
    ngOnInit() {
    	this.downloadConfig = {
			titleBorder: true
    	} as CardConfig
    }
}
