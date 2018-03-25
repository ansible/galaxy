import {
	Component,
    OnInit,
    AfterViewInit
} from '@angular/core';

import {
    Router
} from '@angular/router';

import {
	CardConfig
} from 'patternfly-ng/card/basic-card/card-config';

import { ContentBlocksService } from '../resources/content-blocks/content-blocks.service';

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
    
    downloadContent: string;
    shareContent: string;
    featuredBlogContent: string;
<<<<<<< HEAD
    headerTitle: string = "Home";
    searchText: string = '';

    constructor(
        private contentBlocks: ContentBlocksService,
        private router: Router
=======
	headerTitle: string = "Home";

    constructor(
        private contentBlocks: ContentBlocksService
>>>>>>> Adds dynamic content blocks to UI
    ) {}
    
    ngOnInit() {
        this.contentBlocks.query().subscribe(
            results => {
                results.forEach(result => {
                    switch (result.name) {
                        case 'main-downloads':
                            this.downloadContent = result.content;
                            break;
                        case 'main-share':
                            this.shareContent = result.content;
                            break;
                        case 'main-featured-blog':
                            this.featuredBlogContent = result.content;
                            break
                    }
                });
                this.setCardHeight();
            }
        );
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

    searchContent(): void {
        this.router.navigate(['/search'], {queryParams: {keywords: this.searchText}});
    }

    // private 

    private setCardHeight(): void {
        // Set the cards to a consistent height
        setTimeout(_ => {
            let windowHeight = window.innerHeight;
            let windowWidth = window.innerWidth;
<<<<<<< HEAD
            $('#card-1 .pfng-card').css('height', 'auto');
            $('#card-2 .pfng-card').css('height', 'auto');
            $('#card-3 .pfng-card').css('height', 'auto');
            let height1 = $('#card-1 .pfng-card').height();
            let height2 = $('#card-2 .pfng-card').height();
            let height3 = $('#card-3 .pfng-card').height();
=======
            let height1 = $('#card-1').height();
            let height2 = $('#card-2').height();
            let height3 = $('#card-3').height();
>>>>>>> Adds dynamic content blocks to UI
            let height = Math.max(height1, height2, height3);
            if (windowWidth > 768 && !isNaN(height)) {
                $('#card-1 .pfng-card').css('height', height);
                $('#card-2 .pfng-card').css('height', height);
                $('#card-3 .pfng-card').css('height', height);
<<<<<<< HEAD
=======
            } else {
                $('#card-1 .pfng-card').css('height', 'auto');
                $('#card-2 .pfng-card').css('height', 'auto');
                $('#card-3 .pfng-card').css('height', 'auto');
>>>>>>> Adds dynamic content blocks to UI
            }
        }, 1000);
    }
}
  
<<<<<<< HEAD
  
=======
  
>>>>>>> Adds dynamic content blocks to UI
