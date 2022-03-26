import React from 'react';
import $ from 'jquery';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';

const APP_AUTHOR = "APP_AUTHOR";
const APP_NAME = "APP_NAME";
const APP_VERSION = "APP_VERSION";

class Footer extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            app_author: '',
            app_name: '',
            app_version: ''
        };
    }

    componentDidMount() {
        $.ajax({
            url: '/app_info',
            method: 'GET',
            success: (response) => {
                this.setState({ 
                    app_author: response.APP_AUTHOR,
                    app_name: response.APP_NAME,
                    app_version: response.APP_VERSION
                });
            } 
        })
    }

    render () {

        const display = (
            <Container>
                <Row>
                    This is {this.state.app_name}
                </Row>
                <Row>
                    version {this.state.app_version}
                </Row>
            </Container>
        );

        return (
            <footer className="app_footer">
                <center>
                    {display}
                </center>
            </footer>
        );
    }

}

export default Footer;

