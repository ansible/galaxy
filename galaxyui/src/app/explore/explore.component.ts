import { Component, OnInit } from '@angular/core';
import { Repository } from '../resources/respositories/repository';
import { RepositoryService } from '../resources/respositories/repository.service';
import { ListConfig } from 'patternfly-ng/list/basic-list/list-config';


class TopCard {
  type_name: string;
  type_icon: string;
  name: string;
  count: number;
  children: TopCard[];
  url: string;
}

@Component({
  selector: 'app-explore',
  templateUrl: './explore.component.html',
  styleUrls: ['./explore.component.less']
})
export class ExploreComponent implements OnInit {
  headerTitle = 'Explore';
  mostStarredRepos: TopCard[] = [];
  mostWatchedRepos: TopCard[] = [];


  constructor(
    private repositoryService: RepositoryService,
  ) { }

  ngOnInit() {
    this.getMostStarred();
    this.getMostWatched();
  }

  repositoryToTopCard(repo: Repository, type_name: string, type_icon: string): TopCard {
    console.log(repo);
    let card: TopCard ={
      type_name: type_name,
      type_icon: type_icon,
      name: repo.name,
      count: repo.stargazers_count,
      url: '',
      children: [],
    };

    console.log(card);

    return card;
  }

  getMostStarred(): void {
    this.repositoryService.query({'order_by': '-stargazers_count', 'page_size': '5'})
      .subscribe(repositories => {
        console.log(repositories[0])
        this.mostStarredRepos.push(this.repositoryToTopCard(repositories[0], "Repo", "gear"));
        console.log(this.mostStarredRepos[0]);
        repositories.slice(1,5).forEach(
          repo => this.mostStarredRepos[0].children.push(this.repositoryToTopCard(repo, "", ""))
        );

      });
  }

  getMostWatched(): void {
    this.repositoryService.query({'order_by': '-watchers_count', 'page_size': '5'})
      .subscribe(repositories => {
        console.log(repositories[0])
        this.mostWatchedRepos.push(this.repositoryToTopCard(repositories[0], "Repo", "gear"));
        console.log(this.mostStarredRepos[0]);
        repositories.slice(1,5).forEach(
          repo => this.mostWatchedRepos[0].children.push(this.repositoryToTopCard(repo, "", ""))
        );

      });
  }


}
