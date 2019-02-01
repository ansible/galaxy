import { Component, Input, OnInit } from '@angular/core';

class InfoConfig {
    link: string;
    text: string;
}

@Component({
    selector: 'app-score-bar',
    templateUrl: './score-bar.component.html',
    styleUrls: ['./score-bar.component.less'],
})
export class ScoreBarComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'ScoreBarComponent';

    constructor() {}

    @Input()
    score: number;

    @Input()
    text: string;

    @Input()
    dividend = 5;

    @Input()
    extraInfo: string;

    @Input()
    customTextStyle: string;

    @Input()
    barText: string;

    @Input()
    infoIcon: InfoConfig;

    ngOnInit() {}

    // Calculates the width of the green rating bar.
    getWidthPercentage(rating: number): string {
        return (rating / 5) * 100 + '%';
    }
}
