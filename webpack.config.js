const path = require("path");
const BundleTracker = require("webpack-bundle-tracker");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = {
  mode: process.env.ENV == "production" ? "production" : "development",
  context: __dirname,
  entry: {
    // Non-react bundle
    // This is the main entry point for the non-react bundle
    // It will include all the JS and SCSS files that are not part of the React app
    main: [
      "./front_end/js/application.js",
      "./front_end/stylesheets/application.scss",
    ],
    // React bundle
    // This is the main entry point for the React bundle
    // It will include all the JS and SCSS files that are part of the React app
    react: ["./react_front_end/src/index.js"],
  },
  output: {
    // Where Webpack will compile assets to
    path: path.resolve("./front_end/webpack_bundles/"),
    // Where the compiled assets will be accessed through Django
    // (they are picked up by `collectstatic`)
    publicPath: "/static/webpack_bundles/",
    filename: "[name]-[contenthash].js",
  },

  plugins: [
    new BundleTracker({ path: __dirname, filename: "webpack-stats.json" }),
    new MiniCssExtractPlugin({
      filename: "[name]-[contenthash].css",
      chunkFilename: "[id]-[contenthash].css",
    }),
  ],

  module: {
    rules: [
      // Use Babel to transpile JS/JSX
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
        },
      },
      // Use file-loader to handle image assets
      {
        test: /\.(png|jpe?g|gif|woff2?|svg|ico)$/i,
        use: [
          {
            loader: "file-loader",
            options: {
              // Note: `django-webpack-loader`'s `webpack_static` tag does
              //       not yet pick up versioned assets, so we need to
              //       generate image assets without a hash in the
              //       filename.
              // c.f.: https://github.com/owais/django-webpack-loader/issues/138
              name: "[name].[ext]",
            },
          },
        ],
      },

      // Extract compiled SCSS separately from JS
      {
        test: /\.(s[ac]ss|css)$/i,
        use: [
          {
            loader: MiniCssExtractPlugin.loader,
          },
          "css-loader",
          {
            loader: "sass-loader",
          },
        ],
      },
    ],
  },

  resolve: {
    modules: ["node_modules"],
    extensions: [".js", ".jsx", ".scss"],
  },
};
