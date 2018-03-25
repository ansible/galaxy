import {
	Component,
    OnInit,
    AfterViewInit
} from '@angular/core';

import {
	CardConfig
} from 'patternfly-ng/card/basic-card/card-config';

import * as $ from 'jquery';

@Component({
    selector:    'home',
    templateUrl: './home.component.html',
    styleUrls:   ['./home.component.less']
})
export class HomeComponent implements OnInit, AfterViewInit {

	downloadConfig: CardConfig;
    shareConfig: CardConfig;
    featureConfig: CardConfig;

	headerTitle: string = "Home";

    constructor() {}
    
    ngOnInit() {
    	this.downloadConfig = {
			titleBorder: true
    	} as CardConfig

        this.shareConfig = {
            titleBorder: true
        } as CardConfig

        this.featureConfig = {
            titleBorder: true
        } as CardConfig
    }

    onResize($event) {
        this.setCardHeight();
    }

    ngAfterViewInit() {
        this.setCardHeight();
    }

    // private 

    private setCardHeight(): void {
        // Set the cards to a consistent height
        let windowHeight = window.innerHeight;
        let windowWidth = window.innerWidth;
        let height1 = $('#card-1').height();
        let height2 = $('#card-2').height();
        let height3 = $('#card-3').height();
        let height = Math.max(height1, height2, height3);
        console.log('Set height: ' + height);
        if (windowWidth > 768 && !isNaN(height)) {
            $('#card-1 .pfng-card').css('height', height);
            $('#card-2 .pfng-card').css('height', height);
            $('#card-3 .pfng-card').css('height', height);
        } else {
            $('#card-1 .pfng-card').css('height', 'auto');
            $('#card-2 .pfng-card').css('height', 'auto');
            $('#card-3 .pfng-card').css('height', 'auto');
        }
    }
}
