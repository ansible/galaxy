import * as React from 'react';

interface IRepoScore {
    community_score: any;
    quality_score: any;
    community_survey_count: number;
}

interface IProps {
    repo: IRepoScore;
}

export class Score extends React.Component<IProps, {}> {
    render() {
        const { repo } = this.props;
        let score;

        const survey_count =
            repo.community_survey_count > 3 ? 3 : repo.community_survey_count;

        if (repo.community_score !== null && repo.quality_score !== null) {
            score =
                repo.quality_score * ((6 - survey_count) / 6) +
                repo.community_score * (survey_count / 6);
        } else {
            score = repo.community_score || repo.quality_score;
        }

        if (score !== null) {
            score = Math.round(score * 10) / 10;
        } else {
            return null;
        }

        return (
            <div className='combined-score-wrapper'>
                <div className='score'>
                    <i
                        className={
                            'patternfly-list-additional-override fa ' +
                            this.getScoreColor(score)
                        }
                    />
                    <span className='count-digits'>
                        {score} <span className='denominator'>/ 5</span>
                    </span>
                    <span>Score</span>
                </div>
            </div>
        );
    }

    private getScoreColor(score: number) {
        if (score > 3.5) {
            return 'fa-check-circle score-green';
        }

        if (score >= 1) {
            return 'fa-exclamation-circle score-yellow';
        }

        return 'fa-times-circle score-red';
    }
}
