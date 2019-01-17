import * as React from 'react';
import { Link } from './link';
import './page-header.less';

interface IPageHeaderProp {
    headerIcon: string;
    headerTitle: string;
}

export class PageHeader extends React.Component<IPageHeaderProp, {}> {
    render() {
        const title_list = this.props.headerTitle.split(';');
        let breadcrumbs = [];

        if (this.props.headerIcon) {
            breadcrumbs.push(
                <li>
                    <span className={this.props.headerIcon} />
                </li>,
            );
        }

        if (title_list.length > 1) {
            breadcrumbs.push(
                <li className='show-on-mobile'>
                    <span className='fa fa-angle-double-right' />
                </li>,
            );
        }

        console.log(title_list);

        title_list.forEach((item: string, idx: number) => {
            if (idx % 2) {
                const name = title_list[idx - 1];
                const path = item;
                breadcrumbs.push(
                    <li className='hide-on-mobile'>
                        <Link to={path}>{name}</Link>
                        <span className='separator'>
                            <span className='fa fa-angle-right' />
                        </span>
                    </li>,
                );
            }
            if (idx === title_list.length - 1) {
                const name = item;
                breadcrumbs.push(<li>{name}</li>);
            }
        });

        return (
            <div className='page-header-react-wrapper'>
                <div className='page-header'>
                    <ul className='page-header-list'>{breadcrumbs}</ul>
                </div>
            </div>
        );
    }
}
