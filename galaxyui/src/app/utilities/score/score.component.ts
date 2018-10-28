import { Component, Input, OnInit } from '@angular/core';

@Component({
    selector: 'app-score',
    templateUrl: './score.component.html',
    styleUrls: ['./score.component.less'],
})
export class ScoreComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'ScoreComponent';

    constructor() {}

    @Input()
    quality: number;

    @Input()
    community: number;

    score: number;

    scoreClass: string;

    ngOnInit() {
        if (this.community !== null && this.quality !== null) {
            this.score = (this.community + this.quality) / 2;
        } else {
            this.score = this.community || this.quality;
        }

        this.scoreClass = this.getScoreColor(this.score);

        if (this.score !== null) {
            this.score = Math.round(this.score * 10) / 10;
        }
    }

    getScoreColor(score: number) {
        if (score > 3.5) {
            return 'fa-check-circle score-green';
        }

        if (score >= 1) {
            return 'fa-exclamation-circle score-yellow';
        }

        return 'fa-times-circle score-red';
    }
}
