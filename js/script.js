let fs = window.fs || {};

fs.data = {
    posts: [],
    posts_details: [],
    users_details: [],
};

fs.next_posts_page = null;

fs.fetch_next_posts_page = function() {
    if (fs.next_posts_page === null || fs.next_posts_page === undefined) {
        return new Promise(function(resolve, reject) {
            reject(null);
        });
    }
    return fetch(fs.next_posts_page).then(function(response) {
        if (response.status !== 200) {
            console.log('Error getting posts page:', response.status);
            return;
        }
        return response.json().then(function(data) {
            for (let i=data.posts.length-1; i>=0; i--) {
                fs.data.posts.push(data.posts[i]);
            }
            fs.next_posts_page = data.previous_page;
            return data;
        });
    });
};

fetch('/data/posts.json').then(function(response) {
    if (response.status !== 200) {
        console.log('Error getting main posts page:', response.status);
        return;
    }
    return response.json().then(function(data) {
        fs.next_posts_page = data.last_page;
        return fs.fetch_next_posts_page().then(function() {
            return fs.fetch_next_posts_page().catch(function() {});
        });
    });
});

fs._fetch_details = function(location, id, variable_store) {
    var url = location + id + '.json';
    return fetch(url)
        .then(function(response) {
            if (response.status !== 200) {
                console.log('Error getting details:', response.status);
                return;
            }
            return response.json().then(function(data) {
                variable_store[id] = data;
                return data;
            });
        });
};

fs.get_post_details = function(post_id) {
    if (fs.data.posts_details[post_id] !== undefined) {
        return new Promise(function(resolve, reject) {
            resolve(fs.data.posts_details[post_id])
        });
    } else {
        return fs._fetch_details('/data/posts/', post_id, fs.data.posts_details);
    }
};

fs.get_user_details = function(user_id) {
    if (fs.data.users_details[user_id] !== undefined) {
        return new Promise(function(resolve, reject) {
            resolve(fs.data.users_details[user_id])
        });
    } else {
        return fs._fetch_details('/data/users/', user_id, fs.data.users_details);
    }
};

window.onscroll = function onScroll() {
    if (window.innerHeight + window.pageYOffset >= document.body.offsetHeight) {
        window.onscroll = null;
        fs.fetch_next_posts_page().then(function() {
            window.onscroll = onScroll;
        }).catch(function() {});
    }
};

const Post = {
    props: ['post', 'is_route'],
    data: function() {
        return {
            post_details: null,
        };
    },
    template: `
        <div class="box">
            <article class="media">
                <figure class="media-left">
                    <p class="image is-64x64">
                        <img v-bind:src="post.user.image_64_path">
                    </p>
                </figure>
                <div class="media-content">

                    <div class="content">
                        <router-link v-bind:to="'/user/' + post.user.id"><strong>{{ post.user.full_name }}</strong></router-link> |
                        <small>
                            <time v-bind:title="moment.utc(post.created_date).format('MMMM Do YYYY, h:mm a')">
                                {{ moment.utc(post.created_date).fromNow() }}
                            </time>
                        </small>
                        <br>
                        {{ post.text }}
                    </div>
                    <div>
                        <small>
                            <p>
                                <nav class="level is-mobile">
                                    <div class="level-left">
                                        <router-link class="level-item" v-bind:to="'/post/' + post.id">
                                            <span class="icon is-small">
                                                <i class="fas fa-heart" aria-hidden="true"></i>
                                            </span>
                                            {{ post.like_count }}
                                        </router-link>
                                        <router-link class="level-item" v-bind:to="'/post/' + post.id">
                                            <span class="icon is-small">
                                                <i class="fas fa-comment" aria-hidden="true"></i>
                                            </span>
                                            {{ post.comment_count }}
                                        </router-link>
                                    </div>
                                </nav>
                            </p>
                        </small>
                    </div>

                    <div v-if="post_details">
                        <article v-for="comment in post_details.comments" v-bind:comment="comment" v-bind:key="comment.id" class="media">
                            <figure class="media-left">
                                <p class="image is-48x48">
                                    <img v-bind:src="comment.user.image_64_path">
                                </p>
                            </figure>
                            <div class="media-content">
                                <div class="content">
                                    <router-link v-bind:to="'/user/' + comment.user.id"><strong>{{ comment.user.full_name }}</strong></router-link> |
                                    <small>
                                        <time v-bind:title="moment.utc(comment.created_date).format('MMMM Do YYYY, h:mm a')">
                                            {{ moment.utc(comment.created_date).fromNow() }}
                                        </time>
                                    </small>
                                    <br>
                                    {{ comment.text }}
                                </div>
                            </div>
                        </article>
                    </div>

                </div>

                <div v-if="is_route" class="media-right">
                    <a @click="$router.go(-1)" class="button is-small">
                        <span class="icon is-small">
                            <i class="fas fa-arrow-left"></i>
                        </span>
                    </a>
                    <router-link to="/" class="button is-small">
                        <span class="icon is-small">
                            <i class="fas fa-times"></i>
                        </span>
                    </router-link>
                </div>
            </article>
        </div>
    `,
    created: function() {
        this.fetchData();
    },
    methods: {
        fetchData: function() {
            if (this.is_route === true) {
                let self = this;
                fs.get_post_details(this.post.id).then(function(post_details) {
                    self.post_details = post_details;
                });
            }
        },
    },
};

const PostRoute = {
    data: function() {
        return {
            post: null,
        }
    },
    template: `
        <div class="modal is-active">
            <div class="modal-background"></div>
            <div class="modal-content">
                <post v-if="post" v-bind:post="post" v-bind:is_route="true"></post>
            </div>
        </div>
    `,
    created: function() {
        this.fetchData();
    },
    mounted: function() {
        document.documentElement.classList.add('is-clipped');
    },
    destroyed: function() {
        document.documentElement.classList.remove('is-clipped');
    },
    methods: {
        fetchData: function() {
            let self = this;
            fs.get_post_details(this.$route.params.id).then(function(post) {
                self.post = post;
                document.title = post.user.full_name + ' - post ' + post.id + ' | fakesocial';
            });
        },
    },
    components: {
        'post': Post
    },
};

const UserRoute = {
    data: function() {
        return {
            user: null,
        }
    },
    template: `
        <div v-if="user" class="modal is-active">
            <div class="modal-background"></div>
            <div class="modal-content">
                <div class="box">
                    <article class="media">
                        <figure class="media-left">
                            <img v-bind:src="user.image_256_path">
                        </figure>
                        <div class="media-content">
                            <div class="content">
                                <p>
                                    <strong>{{ user.full_name }}</strong>
                                    <br>
                                    {{ user.job_title }}
                                    <br>
                                    <i class="fas fa-building"></i> <small>{{ user.company_name }}</small>
                                    <br>
                                    <i class="fas fa-map-marker-alt"></i> <small>{{ user.location }}</small>
                                    <br>
                                    <i class="fas fa-user-friends"></i> <small>{{ user.connections.length }}</small>
                                    <br>
                                    <time v-bind:title="moment.utc(user.created_date).format('MMMM Do YYYY, h:mm a')">
                                        Joined {{ moment.utc(user.created_date).fromNow() }}
                                    </time>
                                </p>
                            </div>
                        </div>
                        <div class="media-right">
                            <a @click="$router.go(-1)" class="button is-small">
                                <span class="icon is-small">
                                    <i class="fas fa-arrow-left"></i>
                                </span>
                            </a>
                            <router-link to="/" class="button is-small">
                                <span class="icon is-small">
                                    <i class="fas fa-times"></i>
                                </span>
                            </router-link>
                        </div>
                    </article>
                    <post v-if="user.posts" v-for="post in user.posts" v-bind:post="post" v-bind:key="post.id"></post>
                </div>
            </div>
        </div>
    `,
    created: function() {
        this.fetchData();
    },
    mounted: function() {
        document.documentElement.classList.add('is-clipped');
    },
    destroyed: function() {
        document.documentElement.classList.remove('is-clipped');
    },
    methods: {
        fetchData: function() {
            let self = this;
            fs.get_user_details(this.$route.params.id).then(function(user) {
                self.user = user;
                document.title = user.full_name + ' | fakesocial';
            });
        },
    },
    components: {
        'post': Post,
    },
};

const router = new VueRouter({
    routes: [{
        path: '/post/:id',
        component: PostRoute,
    }, {
        path: '/user/:id',
        component: UserRoute,
    }],
});

router.beforeEach(function(to, from, next) {
    if (to.path === '/') {
        document.title = 'fakesocial';
    }
    next();
});

let app = new Vue({
    el: '#app',
    data: {
        data: fs.data,
    },
    components: {
        'post': Post,
    },
    created: function() {
        let self = this;
        document.onkeydown = function(evt) {
            evt = evt || window.event;
            if (evt.keyCode === 27 && self.$router.currentRoute.path !== '/') {
                self.$router.push('/');
            }
        };
    },
    router: router,
});
