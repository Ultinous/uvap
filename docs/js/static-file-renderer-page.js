const React = require('react');
const fs = require('fs');
const util = require('util');
const path = require('path');
const request = require('request');

const CompLibrary = require(process.cwd() + '/node_modules/docusaurus/lib/core/CompLibrary.js');
const renderMarkdown = require(process.cwd() + '/node_modules/docusaurus/lib/core/renderMarkdown.js');

const Container = CompLibrary.Container;
const MarkdownBlock = CompLibrary.MarkdownBlock;

class StaticFileRendererPage extends React.Component {
  file() {
    const userFilePath = this.props.userFile.replace(process.env.container_website_path, process.env.PWD).replace('website/pages/', 'website/static/_src_')
    const filePath = userFilePath.substring(0, userFilePath.length - 3);
    const fileSource = fs.readFileSync(filePath, 'utf8');
    const fileExtension = path.extname(filePath);
    var fileLanguage;
    switch(fileExtension) {
      case '.proto': fileLanguage = 'protobuf'; break;
      case '.py': fileLanguage = 'python'; break;
      case '.properties': fileLanguage = 'properties'; break;
      default: fileLanguage = 'plaintext'; break;
    }
    return (
      <div>
        <a target="_blank" className="btnDownload" href={filePath.replace(process.env.PWD + '/static/', this.props.config.baseUrl)}></a>
        <div className="static-file-code-block" dangerouslySetInnerHTML={{
          __html: renderMarkdown('```'+ fileLanguage + ' codeBlockCopy\n' + fileSource + '\n```'),
        }}
        />
      </div>
    );
  }

  render() {
    return (
      <div className="docMainWrapper wrapper">
        <Container className="mainContainer documentContainer postContainer">
          <div className="post">
            {this.file()}
          </div>
        </Container>
      </div>
    );
  }
}
module.exports = StaticFileRendererPage;
