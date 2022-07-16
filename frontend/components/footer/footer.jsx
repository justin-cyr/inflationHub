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

        this._isMounted = false;
        this.state = {
            app_author: '',
            app_name: '',
            app_version: ''
        };
    }

    componentDidMount() {
        this._isMounted = true;
        $.ajax({
            url: '/app_info',
            method: 'GET',
            success: (response) => {
                this._isMounted && this.setState({ 
                    app_author: response.APP_AUTHOR,
                    app_name: response.APP_NAME,
                    app_version: response.APP_VERSION
                });
            } 
        })
    }

    componentWillUnmount() {
        this._isMounted = false;
    }

    render () {

        const display = (
            <Container fluid>
                <Row>
                    <p style={{ textAlign: 'center', fontSize: '10px', lineHeight: 0.9}}>
                    This is {this.state.app_name}
                    <br></br>
                    version {this.state.app_version}
                    </p>
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

